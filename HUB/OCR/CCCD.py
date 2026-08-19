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
        try:
            fields[3] = convert_date_format(fields[3])  # Chuyển định dạng ngày sinh
            fields[6] = convert_date_format(fields[6])  # Chuyển định dạng ngày cấp
        except ValueError as e:
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

if __name__ == "__main__":
    # Test
    image_path = r"C:\Users\ADMIN\Pictures\phone\cccd_1.jpg"
    data = read_qr_code(image_path)
    if data:
        print(data)
    else:
        print("Không tìm thấy dữ liệu hợp lệ trong QR code.")