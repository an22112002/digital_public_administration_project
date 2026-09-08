import time

from ..auto_press_keyboard import press_key, reset
from pywinauto import keyboard
import pyperclip

basic_personal_info_fields = ["fullname", "dob", "sex", "CCCD_id", "issue_date", "address", "issue_place"]

# Hàm để điền dữ liệu vào form
async def formInsert(data: list[tuple]):
    for field_type, value in data:
        await press_key(field_type, value)

async def insertSelf(personal_data: dict):
    if not all(field in personal_data for field in basic_personal_info_fields):
        print("Dữ liệu form không đầy đủ. Vui lòng cung cấp tất cả các trường cần thiết.")
        return
    data = [
        ("text", personal_data["fullname"]),
        ("date", personal_data["dob"]),
        ("tab", 2),
        ("text", personal_data["CCCD_id"]),
        ("select", "Thẻ căn cước công dân"),
        ("text", personal_data["CCCD_id"]),
        ("date", personal_data["issue_date"]),
        ("text", personal_data["issue_place"]),
        ("tab", 2),
        ("checkbox", 1),
        ("text", personal_data["address"]),
        ("select", "Việt Nam")
    ]
    if personal_data["isSelf"]:
        data.append(("checkbox", 1))  
        data.append(("tab", 1))
    else:
        data.append(("tab", 1))  
        data.append(("checkbox", 1))  
        data.append(("tab", 1))
    await formInsert(data)

async def insertMain(personal_data: dict):
    if not all(field in personal_data for field in basic_personal_info_fields):
        print("Dữ liệu form không đầy đủ. Vui lòng cung cấp tất cả các trường cần thiết.")
        return
    data = []
    if personal_data["firstTime"]:
        data.append(("checkbox", 1))
    else:
        data.append(("tab", 1))
    data.extend([
        ("text", personal_data["fullname"]),
        ("date", personal_data["dob"]),
        ("tab", 2),
        ("select", personal_data["sex"]),
        ("select", "Kinh"),
        ("select", "Việt Nam"),
        ("text", personal_data["CCCD_id"]),
        ("select", "thẻ căn cước công dân"),
        ("text", personal_data["CCCD_id"]),
        ("date", personal_data["issue_date"]),
        ("tab", 2),
        ("text", personal_data["issue_place"]),
        ("tab", 2),
        ("checkbox", 1),
        ("select", "Việt Nam"),
        ("text", personal_data["address"])
    ])
    await formInsert(data)

# điền thông tin vào form xacNhanTinhTrangHonNhan
async def formXacNhanTinhTrangHonNhanInsert(form_data: list[dict]):
    # reset con trỏ về đầu form
    await reset()
    # kiểm tra thông tin
    if len(form_data) == 0:
        # ko có dữ liệu để điền, bỏ qua
        return
    elif len(form_data) == 1:
        # ko
        return
    else:
        self_person = next((p for p in form_data if p["type"] == "cccd_self"), None)
        main_person = next((p for p in form_data if p["type"] == "cccd_main"), None)
        await insertSelf(self_person)  # điền thông tin cá nhân của người điền
        await insertMain(main_person)  # điền thông tin cá nhân của người còn lại
            