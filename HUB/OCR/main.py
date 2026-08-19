from OCR.CCCD import read_qr_code

def OCR_CCCD(image_path: str) -> dict | None:
    """
    Hàm thực hiện OCR cho CCCD từ hình ảnh.
    :param image_path: Đường dẫn đến hình ảnh chứa CCCD.
    :return: Dictionary chứa thông tin CCCD hoặc None nếu không đọc được.
    """
    try:
        cccd_data = read_qr_code(image_path)
        if cccd_data is None:
            print("Không thể đọc dữ liệu từ QR code.")
            return None
        return cccd_data
    except Exception as e:
        print(f"Lỗi khi thực hiện OCR cho CCCD: {e}")
        return None