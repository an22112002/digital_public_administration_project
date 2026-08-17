import dotenv
import os
import xmltodict

dotenv.load_dotenv("backend/.env")
SCANNER_SAVE_PATH = os.getenv("SCANNER_SAVE_PATH")
SETTING_PATH = os.getenv("SETTING_PATH")

REDIS_HOST, REDIS_PASSWORD, REDIS_PORT = os.getenv("REDIS_HOST"), os.getenv("REDIS_PASSWORD"), os.getenv("REDIS_PORT")

default_settings = {
    "settings": {
        "title": "Phần mềm hỗ trợ nhập liệu hồ sơ hành chính công",
        "naps2_path": "C:\\Program Files (x86)\\NAPS2\\NAPS2.Console.exe",
        "province": "Thành phố Hà Nội",
        "commune": "Phường Ba Đình",
    }
}
# lưu trữ các cài đặt mặc định của ứng dụng, nếu chưa có thì tạo mới
async def create_default_settings():
    await save_settings(default_settings)

async def open_settings():
    if not os.path.exists(SETTING_PATH):
        await create_default_settings()
    with open(SETTING_PATH, "r", encoding="utf-8") as file:
        config_data = xmltodict.parse(file.read())
    return config_data

async def save_settings(config_data):
    with open(SETTING_PATH, "w", encoding="utf-8") as file:
        xml_string = xmltodict.unparse(config_data, pretty=True)
        file.write(xml_string)

if __name__ == "__main__":
    pass