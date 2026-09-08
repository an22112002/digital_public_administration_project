import time

from ..auto_press_keyboard import press_key, reset
from pywinauto import keyboard
import pyperclip

basic_personal_info_fields = ["fullname", "dob", "sex", "CCCD_id", "issue_date", "address", "issue_place"]

# Hàm để điền dữ liệu vào form
async def formInsert(data: list[tuple]):
    for field_type, value in data:
        await press_key(field_type, value)

# Kiểm tra thông tin cá nhân đã được điền sẵn chưa
def is_personal_info_filled() -> bool:
    # thử copy thông tin tiếp theo vào clipboard
    time.sleep(0.05)
    keyboard.send_keys("{TAB}")     # Tab để chuyển đến trường tiếp theo
    time.sleep(0.05)
    keyboard.send_keys("^c")        # Ctrl+C để copy thông tin tiếp theo 
    time.sleep(0.05)
    content = pyperclip.paste()     # Lưu trữ clipboard hiện tại
    time.sleep(0.05)
    keyboard.send_keys("+{TAB}")     # Shift+Tab để quay lại trường trước đó
    time.sleep(0.05)
    if content != "":
        return True
    return False

# điền địa chỉ vào form
async def insertAddress(address: str):
    # đang ở đầu trường họ tên
    data = [
        ("tab", 18),  # tab đến trường địa chỉ
        ("select", "Việt Nam"),
        ("text", address),
    ]
    await formInsert(data)

# nhập thông tin cá nhân của 1 người vào form
async def insertPersonalInfo(personal_data: list[dict]):
    if not all(field in personal_data for field in basic_personal_info_fields):
        print("Dữ liệu form không đầy đủ. Vui lòng cung cấp tất cả các trường cần thiết.")
        return
    data = [
        ("text", personal_data["fullname"]),
        ("date", personal_data["dob"]),
        ("tab", 2),
        ("select", "Kinh"),
        ("select", "Việt Nam"),
        ("text", personal_data["CCCD_id"]),
        ("select", "thẻ căn cước"),
        ("text", personal_data["CCCD_id"]),
        ("date", personal_data["issue_date"]),
        ("tab", 2),
        ("text", personal_data["issue_place"]),
        ("tab", 2),
        ("checkbox", 1),
        ("select", "Việt Nam"),
        ("text", personal_data["address"]),
    ]
    await formInsert(data)

async def fill_extention():
    # các thông tin bổ sung của form ko có trong thông tin cá nhân của vợ
    await press_key("text", "1")  # kết hôn lần thứ mấy
    time.sleep(0.05)
    await press_key("select", "hiện tại chưa đăng ký kết hôn với ai")  # tình trạng hôn nhân
    time.sleep(0.05)

# điền thông tin vào form đăng ký kết hôn
async def formDangKyKetHonInsert(form_data: list[dict]):
    # reset con trỏ về đầu form
    await reset()
    # kiểm tra thông tin
    if len(form_data) == 0:
        # ko có dữ liệu để điền, bỏ qua
        return
    # elif len(form_data) == 1:
    #     # chỉ có 1 người: thông tin cá nhân người điền sẽ được VNeiD điền sẵn, chỉ cần điền thông tin người còn lại
    #     person = form_data[0]
    #     if person["type"] == "cccd_husband":
    #         # người điền là vợ, người cần điền là chồng
    #         # start
    #         await press_key("tab", 20)  # tab đến phần thông tin bổ sung của vợ
    #         await fill_extention()
    #         await insertPersonalInfo(person) # điền thông tin cá nhân của chồng
    #         await fill_extention()
    #         time.sleep(0.05)
    #         keyboard.send_keys("{TAB}")     # Tab để chuyển đến trường tiếp theo
    #         time.sleep(0.05)
    #         keyboard.send_keys("{SPACE}")   # Space để chọn checkbox
    #         # end
    #         return
    #     elif person["type"] == "cccd_wife":
    #         # người điền là chồng, người cần điền là vợ
    #         # start
    #         await insertPersonalInfo(person)
    #         await fill_extention()
    #         await press_key("tab", 20)  # tab đến phần thông tin bổ sung của chồng
    #         await fill_extention()
    #         time.sleep(0.05)
    #         keyboard.send_keys("{TAB}")     # Tab để chuyển đến trường tiếp theo
    #         time.sleep(0.05)
    #         keyboard.send_keys("{SPACE}")   # Space để chọn checkbox
    #         # end
    #         return
    elif len(form_data) == 2:
        # có 2 người: điền thông tin cá nhân của cả 2 người, trong đó có 1 người đã được VNeID điền chỉ cần điền lại địa chỉ
        husband = next((p for p in form_data if p["type"] == "cccd_husband"), None)
        wife = next((p for p in form_data if p["type"] == "cccd_wife"), None)
        # start
        await insertPersonalInfo(wife)  # điền thông tin cá nhân của vợ
        await fill_extention()
        await insertPersonalInfo(husband)  # điền thông tin cá nhân của chồng
        await fill_extention()
        time.sleep(0.05)
        keyboard.send_keys("{TAB}")     # Tab để chuyển đến trường tiếp theo
        time.sleep(0.05)
        keyboard.send_keys("{SPACE}")   # Space để chọn checkbox
        # end
        return

