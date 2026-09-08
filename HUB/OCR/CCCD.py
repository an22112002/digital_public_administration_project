# {
#     "fullname": "",
#     "dob": "",
#     "sex": "",
#     "CCCD_id": "",
#     "issue_date": "",
#     "issue_place": "",
#     "address": "",
# }

import json
from redis.asyncio import Redis

from pyzbar.pyzbar import decode
from PIL import Image
import datetime

from redis import Redis

from OCR.utils import *

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
            "fullname": str(fields[2]).upper(),
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
        "issue_place": "",
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
    data["issue_place"] = "Cục cảnh sát đăng ký quản lý cư trú và dữ liệu quốc gia về dân cư"
    for key in data.keys():
        for r in result:
            value = r.get(key)
            if value:
                data[key] = value
                break
    return data

async def OCR_CCCD2(files: list[str], redis_client: Redis) -> dict | None:
    """
    Hàm thực hiện OCR cho CCCD từ hình ảnh.
    :param files: Danh sách đường dẫn đến các hình ảnh chứa CCCD.
    :return: Dictionary chứa thông tin CCCD hoặc None nếu không đọc được.
    """
    await redis_client.lpush(
        "ocr:jobs",
        json.dumps({
            "job_id": "ocr_001",
            "images_path": files,
        })
    )
    message = await redis_client.blpop(
        "ocr:results",
        timeout=0
    )
    if message is None:
        return None
    _, result_json = message
    result = json.loads(result_json)
    if result.get("job_id") != "ocr_001":
        return None
    if result.get("success") != True:
        return None
    strings = []
    re = result.get("result") # list[dict]
    print(f"re: {re}")
    for r in re:
        x = r.get("texts", [])
        for text in x:
            strings.append(text)
    print(f"strings: {strings}")
    data = emptyOCR_CCCD()
    data["fullname"] = getFullName(strings)
    data["dob"] = getDayOfBirth(strings)
    data["sex"] = getSex(strings)
    data["CCCD_id"] = getCCCD_ID(strings)
    data["issue_date"] = getIssueDate(strings)
    data["address"] = getAddress(strings)
    data["issue_place"] = getIssuePlace(strings)
    return data

async def OCR_CCCD3(files: list[str], redis_client: Redis, id: str) -> dict | None:
    """
    Hàm thực hiện OCR cho CCCD từ hình ảnh.
    :param files: Danh sách đường dẫn đến các hình ảnh chứa CCCD.
    :return: Dictionary chứa thông tin CCCD hoặc None nếu không đọc được.
    """
    # đọc lấy nơi phát hành thẻ
    await redis_client.lpush(
        "ocr:jobs",
        json.dumps({
            "job_id": f"ocr_002_{id}",
            "images_path": files,
        })
    )
    message = await redis_client.blpop(
        "ocr:results",
        timeout=0
    )
    if message is None:
        return None
    _, result_json = message
    result = json.loads(result_json)
    if result.get("job_id") != f"ocr_002_{id}":
        return None
    if result.get("success") != True:
        return None
    strings = []
    re = result.get("result") # list[dict]
    for r in re:
        x = r.get("texts", [])
        for text in x:
            strings.append(text)
    # data lấy từ QR code
    data = emptyOCR_CCCD()
    result = []
    for file in files:
        cccd_data = OCR_CCCD_1_img(file)
        if cccd_data is not None:
            result.append(cccd_data)
    if not result:
        return None
    data["issue_place"] = getIssuePlace(strings)
    for key in data.keys():
        for r in result:
            value = r.get(key)
            if value:
                data[key] = value
                break
    return data

async def OCR_CCCD4(files: list[str], redis_client: Redis, id: str) -> dict | None:
    """
    Hàm thực hiện OCR cho CCCD từ hình ảnh. Thực hiện song song giữa đọc QR code và OCR.
    :param files: Danh sách đường dẫn đến các hình ảnh chứa CCCD.
    :return: Dictionary chứa thông tin CCCD hoặc None nếu không đọc được.
    """
    # đọc lấy nơi phát hành thẻ
    await redis_client.lpush(
        "ocr:jobs",
        json.dumps({
            "job_id": f"ocr_cccd4_{id}",
            "images_path": files,
        })
    )
    message = await redis_client.blpop(
        "ocr:results:" + f"ocr_cccd4_{id}",
        timeout=0
    )
    if message is None:
        return None
    _, result_json = message
    result = json.loads(result_json)
    if result.get("success") != True:
        return None
    strings = []
    re = result.get("result") # list[dict]
    for r in re:
        x = r.get("texts", [])
        for text in x:
            strings.append(text)
    # data lấy từ QR code
    data = emptyOCR_CCCD()
    result = []
    for file in files:
        cccd_data = OCR_CCCD_1_img(file)
        if cccd_data is not None:
            result.append(cccd_data)
    if not result:
        return None
    data["issue_place"] = getIssuePlace(strings)
    for key in data.keys():
        for r in result:
            value = r.get(key)
            if value:
                data[key] = value
                break
    return data
    

# xử lý lấy dữ liệu
def getFullName(cccd_data: list[str]) -> str:
    """
    Hàm lấy họ và tên từ dữ liệu CCCD.
    :param cccd_data: list[str] lấy từ OCR
    :return: Chuỗi họ và tên.
    """
    readyGetFullName = False
    for data in cccd_data:
        if readyGetFullName:
            if isAllUppercase(data) and not isContainsNumber(data):
                return data
        if isSimilar(data, "Họ và tên / Full name"):
            readyGetFullName = True
            continue
    return "UNKNOWN"

def getDayOfBirth(cccd_data: list[str]) -> str:
    ready = False

    for data in cccd_data:

        if ready:
            normalized = normalize_date(data)

            if normalized and isADate(normalized):
                return normalized

        if isSimilar(data, "Ngày sinh / Date of birth"):
            ready = True

    return "00000000"

def getSex(cccd_data: list[str]) -> str:
    """
    Hàm lấy giới tính từ dữ liệu CCCD.
    :param cccd_data: list[str] lấy từ OCR
    :return: Chuỗi giới tính.
    """
    for data in cccd_data:
        if isSimilar(data, "Giới tính / Sex"):
            if "Nam" in data:
                return "Nam"
            elif "Nữ" in data:
                return "Nữ"
    return "UNKNOWN"

def getCCCD_ID(cccd_data: list[str]) -> str:

    for data in cccd_data:

        data = data.strip()

        if (len(data) == 12 and data.isdigit()):
            return data

    return "UNKNOWN"

def getIssueDate(cccd_data: list[str]) -> str:

    for data in cccd_data:

        if isContainSimilarString(data, "Ngày, tháng, năm/ Date, month, year"):

            parts = data.split()

            if not parts:
                continue

            date = normalize_date(parts[-1])

            if date and isADate(date):
                return format_date(date, "%d%m%Y")

    return "00000000"

def getAddress(cccd_data: list[str]) -> str:
    ready_get_address = False

    for data in cccd_data:
        data = data.strip()

        if isSimilar(
            data,
            "Nơi thường trú / Place of residence"
        ):
            ready_get_address = True
            continue

        if ready_get_address:
            print(f"getAddress: {data}")
            if data.count(",") >= 2 and len(data) >= 20:
                return data

    return "UNKNOWN"

def getIssuePlace(cccd_data: list[str]) -> str:
    """
    Hàm lấy nơi cấp từ dữ liệu CCCD.
    :param cccd_data: list[str] lấy từ OCR
    :return: Chuỗi nơi cấp:
    Cục cảnh sát đăng ký quản lý cư trú và dữ liệu quốc gia về dân cư
    Cục cảnh sát quản lý hành chính về trật tự xã hội
    Bộ công an
    Cục quản lý xuất nhập cảnh.
    """
    for i in range(len(cccd_data) - 1):
        s = cccd_data[i] + " " + cccd_data[i + 1]
        if isContainSimilarString(s, "Cục cảnh sát đăng ký quản lý cư trú và dữ liệu quốc gia về dân cư"):
            return "Cục cảnh sát đăng ký quản lý cư trú và dữ liệu quốc gia về dân cư"
        elif isContainSimilarString(s, "Cục cảnh sát quản lý hành chính về trật tự xã hội"):
            return "Cục cảnh sát quản lý hành chính về trật tự xã hội"
        elif isContainSimilarString(s, "Bộ công an"):
            return "Bộ công an"
        elif isContainSimilarString(s, "Cục quản lý xuất nhập cảnh"):
            return "Cục quản lý xuất nhập cảnh"
    return "Cục cảnh sát đăng ký quản lý cư trú và dữ liệu quốc gia về dân cư"

if __name__ == "__main__":
    # Test
    image_path = r"D:\\scanned_files\\patch_1787243092\\images\\page_1.jpg"
    data = read_qr_code(image_path)
    if data:
        print(data)
    else:
        print("Không tìm thấy dữ liệu hợp lệ trong QR code.")