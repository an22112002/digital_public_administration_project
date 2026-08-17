from typing import Literal
from backend.services.settingsServices import getNAPS2Path

# from plugin.Scanner.main import scan_documents_to_folder, check_naps2_installed, get_list_scanner_devices
from plugin.Scanner.mock import scan_documents_to_folder, check_naps2_installed, get_list_scanner_devices

async def checkNAPS2installed():
    # Kiểm tra xem đã cài NAPS2 chưa, trả về tuple (bool, str) với bool là trạng thái cài đặt, str là thông báo
    # path_to_naps2: đường dẫn đến tệp thực thi NAPS2
    path_to_naps2 = await getNAPS2Path()
    result, message = check_naps2_installed(path_to_naps2=path_to_naps2)
    return {"installed": result, "message": message}

async def getScannerDevices(type_driver: str = Literal["wia", "twain", "escl"]) -> list[str]:
    path_to_naps2 = await getNAPS2Path()
    devices = await get_list_scanner_devices(path_to_naps2=path_to_naps2, type_driver=type_driver)
    return devices