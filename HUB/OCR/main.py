from OCR.CCCD import OCR_CCCD

async def processOCR(code: str, files: list[str]) -> dict | None:
    result = []
    if code == "cccd_husband":
        result = OCR_CCCD(files)
        if result is not None:
            result["type"] = "cccd_husband"
            return result
    if code == "cccd_wife":
        result = OCR_CCCD(files)
        if result is not None:
            result["type"] = "cccd_wife"
            return result
    # mở rộng cho các loại tài liệu khác nếu cần
    return None