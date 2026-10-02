from pathlib import Path
from paddleocr import PaddleOCR

BASE_DIR = Path(__file__).resolve().parents[1] / "OCR" / "models"
PPOCRV6_DIR = BASE_DIR / "ppocrv6_vi"

images_path = [r"C:\Users\ADMIN\Pictures\Screenshot_9.jpg", r"C:\Users\ADMIN\Pictures\Screenshot_10.jpg"]

ocr = PaddleOCR(
    text_detection_model_name="PP-OCRv6_medium_det",
    text_recognition_model_name="PP-OCRv6_medium_rec",
    text_recognition_model_dir=str(PPOCRV6_DIR),
)

for image_path in images_path:
    result = ocr.predict(image_path)

    print(f"Results for image: {image_path}")

    for res in result:
        data = res.json["res"]

        texts = data.get("rec_texts", [])
        scores = data.get("rec_scores", [])

        for text, score in zip(texts, scores):
            if text and score > 0:
                print(text)