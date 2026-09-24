from pathlib import Path
from PIL import Image
import numpy as np
import yaml
import time

from vietocr.tool.predictor import Predictor
from vietocr.tool.config import Cfg

from paddleocr import TextDetection

import torch


class TextOCR:
    def __init__(
        self,
        original_image: str,
        box: np.ndarray = None,
        confidence: float = None,
        text: str = None
    ):
        self.image = original_image
        self.box = box
        self.confidence = confidence
        self.text = text


images = [
    r"C:\Users\ADMIN\Pictures\giay_chung_sinh.jpg"
]


# ============================================================
# PATH
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[1] / "OCR" / "models"

PADDLE_DIR = BASE_DIR / "paddle" / "PP-OCRv6_medium_det"
VIETOCR_DIR = BASE_DIR / "vietocr"


# ============================================================
# TIMER
# ============================================================

program_start = time.perf_counter()


# ============================================================
# LOAD VIETOCR
# ============================================================

vietocr_start = time.perf_counter()

config = Cfg.load_config_from_file(
    VIETOCR_DIR / "base.yml"
)

with open(
    VIETOCR_DIR / "vgg-transformer.yml",
    encoding="utf-8"
) as f:
    config.update(yaml.safe_load(f))

config["device"] = "cpu"
config["weights"] = str(
    (VIETOCR_DIR / "vgg_transformer.pth").resolve()
)

rec_model = Predictor(config)

vietocr_load_time = time.perf_counter() - vietocr_start

print(
    f"VietOCR model loaded: "
    f"{vietocr_load_time:.3f}s"
)


# ============================================================
# LOAD PADDLEOCR DETECTION
# ============================================================

paddle_load_start = time.perf_counter()

paddle_td_model = TextDetection(
    model_dir=str(PADDLE_DIR.resolve()),
    device="cpu"
)

paddle_load_time = time.perf_counter() - paddle_load_start

print(
    f"PaddleOCR Detection model loaded: "
    f"{paddle_load_time:.3f}s"
)


# ============================================================
# OCR
# ============================================================

items = []

total_detection_time = 0.0
total_recognition_time = 0.0

total_detection_count = 0
total_recognition_count = 0


for image_path in images:

    print()
    print("=" * 70)
    print(f"IMAGE: {image_path}")

    # --------------------------------------------------------
    # Load image
    # --------------------------------------------------------

    image = Image.open(image_path).convert("RGB")

    # --------------------------------------------------------
    # PADDLEOCR DETECTION
    # --------------------------------------------------------

    detection_start = time.perf_counter()

    results = paddle_td_model.predict(image_path)

    detection_time = time.perf_counter() - detection_start

    total_detection_time += detection_time

    print(
        f"Paddle Detection: "
        f"{detection_time:.3f}s"
    )

    # --------------------------------------------------------
    # Extract detection results
    # --------------------------------------------------------

    for result in results:

        data = result.json

        res = data["res"]

        polygons = res.get("dt_polys", [])
        scores = res.get("dt_scores", [])

        for polygon, score in zip(polygons, scores):

            score = float(score)

            # Detection threshold
            if score < 0.3:
                continue

            polygon = np.array(
                polygon,
                dtype=np.int32
            )

            # ------------------------------------------------
            # Polygon -> bounding rectangle
            # ------------------------------------------------

            x1 = max(0, int(np.min(polygon[:, 0])))
            y1 = max(0, int(np.min(polygon[:, 1])))

            x2 = min(image.width, int(np.max(polygon[:, 0])))
            y2 = min(image.height, int(np.max(polygon[:, 1])))

            # tránh box lỗi
            if x2 <= x1 or y2 <= y1:
                continue

            # ------------------------------------------------
            # Crop text region
            # ------------------------------------------------

            crop = image.crop(
                (x1, y1, x2, y2)
            )

            # ------------------------------------------------
            # VIETOCR RECOGNITION
            # ------------------------------------------------

            recognition_start = time.perf_counter()

            text = rec_model.predict(crop)

            recognition_time = (
                time.perf_counter()
                - recognition_start
            )

            total_recognition_time += recognition_time
            total_recognition_count += 1

            # ------------------------------------------------
            # Create TextOCR
            # ------------------------------------------------

            item = TextOCR(
                original_image=image_path,
                box=polygon,
                confidence=score,
                text=text
            )

            items.append(item)

            print(
                f"  [{total_recognition_count:03d}] "
                f"det={score:.3f} "
                f"rec={recognition_time:.3f}s "
                f"text={text!r}"
            )


# ============================================================
# TOTAL
# ============================================================

total_time = time.perf_counter() - program_start


print()
print("=" * 70)
print("OCR SUMMARY")
print("=" * 70)

print(
    f"VietOCR load       : "
    f"{vietocr_load_time:.3f}s"
)

print(
    f"PaddleOCR load     : "
    f"{paddle_load_time:.3f}s"
)

print(
    f"Detection total    : "
    f"{total_detection_time:.3f}s"
)

print(
    f"Recognition total  : "
    f"{total_recognition_time:.3f}s"
)

print(
    f"Detected boxes     : "
    f"{len(items)}"
)

print(
    f"Recognition count  : "
    f"{total_recognition_count}"
)

print(
    f"TOTAL              : "
    f"{total_time:.3f}s"
)


# ============================================================
# PRINT FINAL TEXTOCR LIST
# ============================================================

print()
print("=" * 70)
print("TextOCR ITEMS")
print("=" * 70)

for i, item in enumerate(items):

    print(
        f"[{i}] "
        f"text={item.text!r} "
        f"confidence={item.confidence:.3f} "
        f"box={item.box.tolist()}"
    )
