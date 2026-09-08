import dotenv
import asyncio
import os
import xmltodict
from pathlib import Path

# Load .env file if it exists (for local development)
env_file = Path("backend/.env")
if env_file.exists():
    dotenv.load_dotenv(env_file)

# Use environment variables (with fallback defaults for local development)
SETTING_PATH = "./settings.xml"

REDIS_HOST = "localhost"
REDIS_PASSWORD = "redispassword"
REDIS_PORT = 6380

default_settings = {
    "settings": {
        "title": "Phần mềm hỗ trợ nhập liệu hồ sơ hành chính công",
        "naps2_path": "C:\\Program Files (x86)\\NAPS2\\NAPS2.Console.exe",
        "province": "Thành phố Hà Nội",
        "commune": "Phường Ba Đình",
        "scanner_save_path": r"D:\scanned_files",
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

async def get_scanner_save_path():
    settings = await open_settings()
    return settings["settings"]["scanner_save_path"]

def setup():
    global SCANNER_SAVE_PATH
    SCANNER_SAVE_PATH = asyncio.run(get_scanner_save_path())
    os.makedirs(SCANNER_SAVE_PATH, exist_ok=True)

setup()

if __name__ == "__main__":
    pass