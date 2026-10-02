import time

from ..auto_press_keyboard import press_key, reset
from pywinauto import keyboard
import pyperclip

basic_personal_info_fields = ["type_document", "fullname", "dob", "sex", "id_number", "issue_date", "address", "issue_place"]
cnkh_info_fields = ["commune", "province", "number", "serial_number", "registration_date"]

# Hàm để điền dữ liệu vào form
async def formInsert(data: list[tuple]):
    for field_type, value in data:
        await press_key(field_type, value)

# nhập thông tin cá nhân của 1 người vào form
async def insertWifeInfo(personal_data: list[dict]):
    if not all(field in personal_data for field in basic_personal_info_fields):
        print("Dữ liệu form không đầy đủ. Vui lòng cung cấp tất cả các trường cần thiết.")
        return
    data = [
        ("text", personal_data["fullname"]),
        ("date", personal_data["dob"]),
        ("tab", 2),
        ("select", "Kinh"),
        ("select", "Việt Nam"),
        ("text", personal_data["id_number"]),
        ("select", personal_data["type_document"]),
        ("text", personal_data["id_number"]),
        ("date", personal_data["issue_date"]),
        ("tab", 2),
        ("text", personal_data["issue_place"]),
        ("tab", 2),
        ("checkbox", 1),
        ("select", "Việt Nam"),
        ("text", personal_data["address"]),
        
    ]
    await formInsert(data)

async def insertHusbandInfo(personal_data: list[dict]):
    if not all(field in personal_data for field in basic_personal_info_fields):
        print("Dữ liệu form không đầy đủ. Vui lòng cung cấp tất cả các trường cần thiết.")
        return
    data = [
        ("text", personal_data["fullname"]),
        ("date", personal_data["dob"]),
        ("tab", 2),
        ("select", "Kinh"),
        ("select", "Việt Nam"),
        ("text", personal_data["id_number"]),
        ("select", personal_data["type_document"]),
        ("text", personal_data["id_number"]),
        ("date", personal_data["issue_date"]),
        ("tab", 2),
        ("text", personal_data["issue_place"]),
        ("tab", 2),
        ("checkbox", 1),
        ("select", "Việt Nam"),
        ("text", personal_data["address"]),
    ]
    await formInsert(data)

async def insertCNKHInfo(info: dict):
    step = []
    if info["province"] and info["province"] != "UNKNOWN":
        step.append(("select", info["province"]))
    else:
        step.append(("tab", 1))
    if info["commune"] and info["commune"] != "UNKNOWN":
        step.append(("select", info["commune"]))
    else:
        step.append(("tab", 1))
    if info["registration_date"] and info["registration_date"] != "00000000":
        step.append(("date", info["registration_date"]))
        step.append(("tab", 2))
    else:
        step.append(("tab", 5))
    if info["number"] and info["number"] != "UNKNOWN":
        step.append(("text", info["number"]))
    else:
        step.append(("tab", 1))
    if info["serial_number"] and info["serial_number"] != "UNKNOWN":
        step.append(("text", info["serial_number"]))
    else:
        step.append(("tab", 1))
    await formInsert(step)

async def fill_extension():
    # các thông tin bổ sung của form ko có trong thông tin cá nhân của vợ
    await press_key("text", "1")  # kết hôn lần thứ mấy
    time.sleep(0.05)
    await press_key("select", "Hiện tại đang có vợ/chồng")  # tình trạng hôn nhân
    time.sleep(0.05)

async def setCopyNumber1(number: int):
    data = [
        ("tab", 10),
        ("checkbox", 1),
        ("text", str(number))
    ]
    await formInsert(data)

async def setCopyNumber2(number: int):
    data = [
        ("tab", 1),
        ("checkbox", 1),
        ("text", str(number))
    ]
    await formInsert(data)

# điền thông tin vào form đăng ký kết hôn
async def formDangKyLaiKetHonInsert(form_data: list[dict]):
    # reset con trỏ về đầu form
    await reset()
    # kiểm tra thông tin
    if len(form_data) == 0:
        return
    elif len(form_data) == 2:
        # có 2 người: điền thông tin cá nhân của cả 2 người, trong đó có 1 người đã được VNeID điền chỉ cần điền lại địa chỉ
        husband = next((p for p in form_data if p["type"] == "cccd_husband"), None)
        wife = next((p for p in form_data if p["type"] == "cccd_wife"), None)
        # start
        await insertWifeInfo(wife)  # điền thông tin cá nhân của vợ
        await fill_extension()
        await insertHusbandInfo(husband)  # điền thông tin cá nhân của chồng
        await fill_extension()
        time.sleep(0.05)
        keyboard.send_keys("{TAB}")     # Tab để chuyển đến trường tiếp theo
        time.sleep(0.05)
        keyboard.send_keys("{SPACE}")   # Space để chọn checkbox
        await setCopyNumber1(1)  # điền số bản sao
        # end
        return
    elif len(form_data) == 3:
        # có 2 người: điền thông tin cá nhân của cả 2 người, trong đó có 1 người đã được VNeID điền chỉ cần điền lại địa chỉ
        husband = next((p for p in form_data if p["type"] == "cccd_husband"), None)
        wife = next((p for p in form_data if p["type"] == "cccd_wife"), None)
        cnkh = next((p for p in form_data if p["type"] == "cnkh"), None)
        # start
        await insertWifeInfo(wife)  # điền thông tin cá nhân của vợ
        await fill_extension()
        await insertHusbandInfo(husband)  # điền thông tin cá nhân của chồng
        await fill_extension()
        time.sleep(0.05)
        keyboard.send_keys("{TAB}")     # Tab để chuyển đến trường tiếp theo
        time.sleep(0.05)
        keyboard.send_keys("{SPACE}")   # Space để chọn checkbox
        await insertCNKHInfo(cnkh)  # điền thông tin CNKH
        await setCopyNumber2(1)  # điền số bản sao
        # end
        return