# {
#     "fullname": "",
#     "dob": "",
#     "sex": "",
#     "CCCD_id": "",
#     "issue_date": "",
#     "address": "",
# }

from pyzbar.pyzbar import decode
from PIL import Image
import datetime

# Chuyển đúng định dạng ngày tháng từ ddmmyyyy sang yyyy-mm-dd
def convert_date_format(date_str: str) -> str:
    if len(date_str) != 8:
        raise ValueError("Định dạng ngày tháng không hợp lệ")
    day = date_str[0:2]
    month = date_str[2:4]
    year = date_str[4:8]
    # Kiểm tra ngày tháng có tồn tại không
    try:
        datetime.datetime(int(year), int(month), int(day))
    except ValueError:
        raise ValueError("Ngày tháng không hợp lệ")
    return f"{year}-{month}-{day}"

# Tách dữ liệu từ QR code thành các trường thông tin
def process_data_from_qr_code(data: str) -> dict | None:
    try:
        fields = data.split('|')
        if len(fields) < 7:
            return None

        return {
            "CCCD_id": fields[0],
            "fullname": fields[2],
            "dob": fields[3],
            "sex": fields[4],
            "address": fields[5],
            "issue_date": fields[6],
        }
    except Exception:
        return None

def read_qr_code(image_path) -> dict | None:
    results = decode(Image.open(image_path))

    for result in results:
        data = result.data.decode('utf-8')
        try:
            processed_data = process_data_from_qr_code(data)
            if processed_data:
                return processed_data
        except ValueError as e:
            print(f"Lỗi khi xử lý dữ liệu QR code: {e}")
            return None

    return None

def emptyOCR_CCCD() -> dict:
    """
    Hàm trả về một dictionary rỗng cho trường hợp không có dữ liệu OCR.
    :return: Dictionary rỗng.
    """
    return {
        "fullname": "",
        "dob": "",
        "sex": "",
        "CCCD_id": "",
        "issue_date": "",
        "address": "",
    }

def OCR_CCCD_1_img(image_path: str) -> dict | None:
    """
    Hàm thực hiện OCR cho CCCD từ hình ảnh.
    :param image_path: Đường dẫn đến hình ảnh chứa CCCD.
    :return: Dictionary chứa thông tin CCCD hoặc None nếu không đọc được.
    """
    try:
        cccd_data = read_qr_code(image_path)
        if cccd_data is None:
            print(f"Không thể đọc dữ liệu từ QR code. {image_path}")
            return None
        return cccd_data
    except Exception as e:
        # print(f"Lỗi khi thực hiện OCR cho CCCD: {e}")
        return None

def OCR_CCCD(files: list[str]) -> dict | None:
    """
    Hàm thực hiện OCR cho CCCD từ hình ảnh.
    :param files: Danh sách đường dẫn đến các hình ảnh chứa CCCD.
    :return: Dictionary chứa thông tin CCCD hoặc None nếu không đọc được.
    """
    result = []
    for file in files:
        cccd_data = OCR_CCCD_1_img(file)
        if cccd_data is not None:
            result.append(cccd_data)
    if not result:
        return None
    data = emptyOCR_CCCD()
    for key in data.keys():
        for r in result:
            value = r.get(key)
            if value:
                data[key] = value
                break
    return data

if __name__ == "__main__":
    # Test
    image_path = r"D:\\scanned_files\\patch_1787243092\\images\\page_1.jpg"
    data = read_qr_code(image_path)
    if data:
        print(data)
    else:
        print("Không tìm thấy dữ liệu hợp lệ trong QR code.")