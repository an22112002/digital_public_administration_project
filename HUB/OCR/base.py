TESSERACT = r"D:\Tesseract-OCR\tesseract.exe"

def tesseract_OCR_execute(path_to_tesseract: str, crop_path: str, language: str = "vie") -> str:
    cmd = [
    TESSERACT,
    crop_path,
    "stdout",
    "-l", language,
    "--psm", "7",
    "-c", "tessedit_char_whitelist=0123456789",
]

