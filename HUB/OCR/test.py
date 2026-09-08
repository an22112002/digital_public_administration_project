import cv2
import numpy as np

from PIL import Image

from paddleocr import TextDetection

from vietocr.tool.config import Cfg
from vietocr.tool.predictor import Predictor

from pathlib import Path

import traceback

import yaml

# ============================================================
# 1. LOAD MODELS - CHỈ LOAD 1 LẦN
# ============================================================

print("Loading Paddle detector...")

det_model = TextDetection(
    model_name="PP-OCRv6_medium_det"
)


print("Loading VietOCR...")

BASE_DIR = Path("./OCR/models/vietocr")

base_config = Cfg.load_config_from_file(
    BASE_DIR / "base.yml"
)

with open(BASE_DIR / "vgg-transformer.yml", encoding="utf-8") as f:
    model_config = yaml.safe_load(f)

base_config.update(model_config)

config = base_config

config["device"] = "cpu"
config["weights"] = str(
    (BASE_DIR / "vgg_transformer.pth").resolve()
)

rec_model = Predictor(config)


# ============================================================
# 2. PADDLE DETECTION
# ============================================================

def detect_lines(image_path: str):

    results = det_model.predict(
        image_path
    )

    items = []

    for result in results:

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

    # SORT từ trên xuống dưới,
    # trái sang phải
    items.sort(
        key=lambda x: (
            x["y1"],
            x["x1"]
        )
    )

    return items


# ============================================================
# 3. CROP POLYGON
# ============================================================

def crop_polygon(
    image,
    polygon,
    padding=5
):

    polygon = np.array(
        polygon,
        dtype=np.int32
    )

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

    # polygon về tọa độ crop
    local_polygon = polygon.copy()

    local_polygon[:, 0] -= x1
    local_polygon[:, 1] -= y1

    # mask
    mask = np.zeros(
        crop.shape[:2],
        dtype=np.uint8
    )

    cv2.fillPoly(
        mask,
        [local_polygon],
        255
    )

    # nền trắng
    result = np.ones_like(
        crop
    ) * 255

    result[
        mask > 0
    ] = crop[
        mask > 0
    ]

    return result


# ============================================================
# 4. VIETOCR
# ============================================================

def vietocr_predict(img):

    rgb = cv2.cvtColor(
        img,
        cv2.COLOR_BGR2RGB
    )

    pil = Image.fromarray(rgb)

    text = rec_model.predict(
        pil
    )

    return text.strip()


# ============================================================
# 5. TẠO 3 VERSION
# ============================================================

def make_versions(crop):

    # --------------------------------------------------------
    # RAW
    # --------------------------------------------------------

    raw = crop.copy()


    # --------------------------------------------------------
    # GRAY
    # --------------------------------------------------------

    gray = cv2.cvtColor(
        crop,
        cv2.COLOR_BGR2GRAY
    )

    gray_bgr = cv2.cvtColor(
        gray,
        cv2.COLOR_GRAY2BGR
    )


    # --------------------------------------------------------
    # UPSCALE
    # --------------------------------------------------------

    upscale = cv2.resize(
        gray_bgr,
        None,
        fx=3,
        fy=3,
        interpolation=cv2.INTER_CUBIC
    )

    return (
        raw,
        gray_bgr,
        upscale
    )


# ============================================================
# 6. VOTE
# ============================================================

def vote_text(
    text_raw,
    text_gray,
    text_upscale
):

    texts = [
        text_raw.strip(),
        text_gray.strip(),
        text_upscale.strip()
    ]

    # 2/3 kết quả giống nhau
    for text in texts:

        if not text:
            continue

        if texts.count(text) >= 2:
            return text

    # Nếu cả 3 khác nhau
    # tạm thời ưu tiên UPSCALE
    if text_upscale:
        return text_upscale

    if text_gray:
        return text_gray

    return text_raw


# ============================================================
# 7. PIPELINE
# ============================================================

def pipeline(
    images_path: list[str]
):
    """
    Toàn bộ pipeline OCR:

    images_path:
        list[str]

    Pipeline:

        image
          ↓
        PaddleOCR detection
          ↓
        detect text lines
          ↓
        crop polygon
          ↓
        RAW / GRAY / UPSCALE
          ↓
        VietOCR
          ↓
        vote
          ↓

    Return:

        [
            {
                "image_path": str,
                "texts": list[str]
            }
        ]
    """

    all_results = []

    for image_index, image_path in enumerate(
        images_path
    ):

        print()
        print("=" * 100)
        print(
            f"IMAGE [{image_index + 1}/{len(images_path)}]"
        )
        print(
            image_path
        )
        print("=" * 100)


        # ====================================================
        # LOAD IMAGE
        # ====================================================

        image = cv2.imread(
            image_path
        )

        if image is None:

            print(
                f"[ERROR] Không đọc được: {image_path}"
            )

            all_results.append({
                "image_path": image_path,
                "texts": []
            })

            continue


        # ====================================================
        # PADDLE DETECTION
        # ====================================================

        items = detect_lines(
            image_path
        )

        print(
            f"Detected {len(items)} lines"
        )


        texts = []


        # ====================================================
        # OCR TỪNG LINE
        # ====================================================

        for index, item in enumerate(
            items
        ):

            crop = crop_polygon(
                image,
                item["polygon"],
                padding=5
            )

            if crop is None:
                continue


            # =================================================
            # 3 VERSION
            # =================================================

            raw, gray, upscale = make_versions(
                crop
            )


            # =================================================
            # VIETOCR
            # =================================================

            text_raw = vietocr_predict(
                raw
            )

            text_gray = vietocr_predict(
                gray
            )

            text_upscale = vietocr_predict(
                upscale
            )


            # =================================================
            # VOTE
            # =================================================

            text = vote_text(
                text_raw,
                text_gray,
                text_upscale
            )


            texts.append(
                text
            )


            # =================================================
            # DEBUG
            # =================================================

            print()

            # print(
            #     f"[{index}] "
            #     f"det={item['score']:.3f}"
            # )

            # print(
            #     f"RAW     : {text_raw}"
            # )

            print(
                f"{text_gray}"
            )

            # print(
            #     f"UPSCALE : {text_upscale}"
            # )

            # print(
            #     f"VOTE    : {text}"
            # )

            # print(
            #     "-" * 100
            # )


        # ====================================================
        # RESULT
        # ====================================================

        all_results.append({
            "image_path": image_path,
            "texts": texts
        })


    return all_results

if __name__ == "__main__":
    try:

        images_path = [r"C:\Users\ADMIN\Pictures\phone\cccd_1.jpg", r"C:\Users\ADMIN\Pictures\phone\cccd_2.jpg"]

        results = pipeline(
            images_path
        )

        print()
        print("=" * 100)
        print("RESULTS")
        print("=" * 100)

        for result in results:

            print(
                f"IMAGE: {result['image_path']}"
            )

            for text in result["texts"]:
                print(
                    f"{text}"
                )

            print("-" * 100)
    except Exception as e:
        print(
            "[ERROR] "
            f"{e}"
        )

        traceback.print_exc()