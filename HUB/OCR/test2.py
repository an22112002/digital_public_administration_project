import pymupdf
from vietocr.tool.predictor import Predictor
from vietocr.tool.config import Cfg
from PIL import Image

import paddle
import torch

from pathlib import Path

def splitPDF(pdf_path: str, begin_int: int, output_folder: str):
    output_path = Path(output_folder)
    output_path.mkdir(parents=True, exist_ok=True)

    pdf = pymupdf.open(pdf_path)

    try:
        for i, page in enumerate(pdf):
            pix = page.get_pixmap(dpi=300)

            image_path = output_path / f"page_{i + begin_int}.jpg"

            pix.save(str(image_path))

    finally:
        pdf.close()

splitPDF(r"C:\Users\ADMIN\Downloads\lily.pdf", 1, r"C:\Users\ADMIN\Pictures")