from pathlib import Path

from redis.asyncio import Redis
import json, asyncio
import traceback
import cv2
import numpy as np

from PIL import Image

from paddleocr import TextDetection

from redis import Redis
from vietocr.tool.config import Cfg
from vietocr.tool.predictor import Predictor
import yaml
import sys
from backend.log.main import log_exception

def get_base_dir() -> Path:
    if getattr(sys, "frozen", False):
        # PyInstaller EXE
        return Path(sys.executable).parent / "_internal"

    # DEV: thư mục gốc của project HUB
    return Path(__file__).resolve().parents[2]

BASE_DIR = get_base_dir() / "OCR" / "models"

PADDLE_DIR = BASE_DIR / "paddle" / "PP-OCRv6_medium_det"
VIETOCR_DIR = BASE_DIR / "vietocr"

class OCRWorker:

    def __init__(self, redis_client: Redis, debug: bool = False):
        self.redis_client = redis_client
        self.debug = debug

        self.running = False

        self.det_model = None
        self.rec_model = None

    # =========================================================
    # LOAD MODELS
    # =========================================================

    def load_models(self):
        if self.debug:
            print("[OCR] Loading Paddle detector...")

        self.det_model = TextDetection(
            model_dir=str(PADDLE_DIR.resolve())
            # model_dir=str(PADDLE_DIR.resolve()),
            # model_name="PP-OCRv5_mobile_det"
        )

        if self.debug:
            print("[OCR] Loading VietOCR...")

        base_config = Cfg.load_config_from_file(
            VIETOCR_DIR / "base.yml"
        )

        with open(VIETOCR_DIR / "vgg-transformer.yml", encoding="utf-8") as f:
            model_config = yaml.safe_load(f)

        base_config.update(model_config)

        config = base_config

        config["device"] = "cpu"
        config["weights"] = str(
            (VIETOCR_DIR / "vgg_transformer.pth").resolve()
        )

        self.rec_model = Predictor(
            config
        )

        if self.debug:
            print("[OCR] Models loaded")

    # =========================================================
    # PROCESS
    # =========================================================

    def process(
        self,
        images_path: list[str]
    ):
        """
        Pipeline:

            images
                ↓
            PaddleOCR detection
                ↓
            text polygons
                ↓
            crop
                ↓
            GRAY
                ↓
            VietOCR
                ↓
            result

        Return:

        [
            {
                "image_path": "...",
                "texts": [
                    "...",
                    "...",
                    ...
                ]
            }
        ]
        """

        results = []

        for image_path in images_path:

            if self.debug:
                print(
                    f"[OCR] Processing: {image_path}"
                )

            # =================================================
            # LOAD IMAGE
            # =================================================

            image = cv2.imread(
                image_path
            )

            if image is None:

                results.append({
                    "image_path": image_path,
                    "texts": [],
                    "error": "cannot read image"
                })

                continue

            # =================================================
            # PADDLE DETECTION
            # =================================================

            paddle_results = self.det_model.predict(
                image_path
            )

            items = []

            for result in paddle_results:

                data = result.json
                res = data["res"]

                polygons = res.get(
                    "dt_polys",
                    []
                )

                scores = res.get(
                    "dt_scores",
                    []
                )

                for polygon, score in zip(
                    polygons,
                    scores
                ):

                    score = float(score)

                    # Detection threshold
                    if score < 0.3:
                        continue

                    polygon = np.array(
                        polygon,
                        dtype=np.int32
                    )

                    items.append({
                        "polygon": polygon,
                        "score": score,

                        "x1": int(
                            polygon[:, 0].min()
                        ),

                        "y1": int(
                            polygon[:, 1].min()
                        )
                    })

            # =================================================
            # SORT
            # =================================================

            items.sort(
                key=lambda x: (
                    x["y1"],
                    x["x1"]
                )
            )

            texts = []

            # =================================================
            # VIETOCR
            # =================================================

            for item in items:

                crop = self.crop_polygon(
                    image,
                    item["polygon"]
                )

                if crop is None:
                    continue

                # -------------------------------------------------
                # GRAY
                # -------------------------------------------------

                gray = cv2.cvtColor(
                    crop,
                    cv2.COLOR_BGR2GRAY
                )

                # VietOCR đang nhận PIL RGB/BGR conversion
                # nên chuyển grayscale -> BGR
                gray_bgr = cv2.cvtColor(
                    gray,
                    cv2.COLOR_GRAY2BGR
                )

                # -------------------------------------------------
                # VIETOCR
                # -------------------------------------------------

                text = self.predict(
                    gray_bgr
                )

                texts.append(
                    text
                )

                # -------------------------------------------------
                # DEBUG
                # -------------------------------------------------

                if self.debug:
                    print(
                        f"[OCR] "
                        f"det={item['score']:.3f} "
                        f"text={text}"
                    )

            # =================================================
            # RESULT
            # =================================================

            results.append({
                "image_path": image_path,
                "texts": texts
            })

        return results

    # =========================================================
    # VIETOCR
    # =========================================================

    def predict(
        self,
        image
    ):

        # BGR -> RGB
        rgb = cv2.cvtColor(
            image,
            cv2.COLOR_BGR2RGB
        )

        pil = Image.fromarray(
            rgb
        )

        text = self.rec_model.predict(
            pil
        )

        return text.strip()

    # =========================================================
    # CROP POLYGON
    # =========================================================

    @staticmethod
    def crop_polygon(
        image,
        polygon,
        padding=5
    ):

        polygon = np.array(
            polygon,
            dtype=np.int32
        )

        # Bounding rectangle
        x, y, w, h = cv2.boundingRect(
            polygon
        )

        x1 = max(
            0,
            x - padding
        )

        y1 = max(
            0,
            y - padding
        )

        x2 = min(
            image.shape[1],
            x + w + padding
        )

        y2 = min(
            image.shape[0],
            y + h + padding
        )

        crop = image[
            y1:y2,
            x1:x2
        ]

        if crop.size == 0:
            return None

        # =====================================================
        # Polygon -> local coordinate
        # =====================================================

        local_polygon = polygon.copy()

        local_polygon[:, 0] -= x1
        local_polygon[:, 1] -= y1

        # =====================================================
        # MASK
        # =====================================================

        mask = np.zeros(
            crop.shape[:2],
            dtype=np.uint8
        )

        cv2.fillPoly(
            mask,
            [local_polygon],
            255
        )

        # =====================================================
        # WHITE BACKGROUND
        # =====================================================

        result = np.ones_like(
            crop
        ) * 255

        result[
            mask > 0
        ] = crop[
            mask > 0
        ]

        return result

    # =========================================================
    # ASYNC RUN
    # =========================================================

    async def run(self):

        self.running = True

        await self.redis_client.hset(
            "worker:ocr",
            "running",
            "1"
        )

        print(
            "[OCR WORKER] Starting..."
        )

        try:

            # ========================================
            # LOAD MODEL
            # ========================================

            self.load_models()

            print(
                "[OCR WORKER] Ready"
            )

            # ========================================
            # MAIN LOOP
            # ========================================

            while True:

                # ====================================
                # CHECK ALLOW
                # ====================================

                allow = await self.redis_client.hget(
                    "worker:ocr",
                    "allow"
                )

                if str(allow) != "1":

                    print(
                        "[OCR WORKER] "
                        "allow=False, stopping..."
                    )

                    break

                # ====================================
                # GET JOB
                # ====================================

                message = await self.redis_client.blpop(
                    "ocr:jobs",
                    timeout=1
                )

                if not message:
                    continue

                _, raw_data = message

                job = json.loads(
                    raw_data
                )

                job_id = job["job_id"]

                images_path = job[
                    "images_path"
                ]
                if self.debug:
                    print(
                        f"[OCR WORKER] "
                        f"Job: {job_id}"
                    )

                # ====================================
                # OCR
                # ====================================

                try:

                    result = self.process(
                        images_path
                    )
                    if self.debug:
                        print(
                            f"[OCR WORKER] "
                            f"result: {result}"
                        )

                    await self.redis_client.lpush(
                        "ocr:results:" + job_id,
                        json.dumps(
                            {
                                "job_id": job_id,
                                "success": True,
                                "result": result
                            },
                            ensure_ascii=False
                        )
                    )

                    if self.debug:
                        print("[OCR WORKER] "
                            f"Job {job_id} completed"
                        )

                except Exception as e:

                    log_exception(e, "worker")
                    traceback.print_exc()

                    await self.redis_client.lpush(
                        "ocr:results:" + job_id,
                        json.dumps(
                            {
                                "job_id": job_id,
                                "success": False,
                                "error": str(e)
                            },
                            ensure_ascii=False
                        )
                    )

        except asyncio.CancelledError:

            print(
                "[OCR WORKER] Cancelled"
            )

            raise

        except Exception as e:

            log_exception(e, "worker")
            traceback.print_exc()

        finally:

            self.running = False

            await self.redis_client.hset(
                "worker:ocr",
                "running",
                "0"
            )

            print(
                "[OCR WORKER] Stopped"
            )