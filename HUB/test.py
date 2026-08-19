import asyncio
import pymupdf
from pathlib import Path


def splitPDF(pdf_path: str, output_folder: str):
    output_path = Path(output_folder)
    output_path.mkdir(parents=True, exist_ok=True)

    pdf = pymupdf.open(pdf_path)

    try:
        for i, page in enumerate(pdf):
            pix = page.get_pixmap(dpi=300)

            image_path = output_path / f"page_{i + 1}.jpg"

            pix.save(str(image_path))

    finally:
        pdf.close()

async def test_splitPDF():
    pdf_path = r"D:\test\test.pdf"
    output_folder = r"D:\test_pdf"
    await splitPDF(pdf_path, output_folder)
    return output_folder

if __name__ == "__main__":
    asyncio.run(test_splitPDF())