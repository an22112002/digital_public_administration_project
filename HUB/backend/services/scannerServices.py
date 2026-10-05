# from typing import Literal
# from backend.services.settingsServices import getNAPS2Path
# from plugin.Scanner.main import check_naps2_installed, get_list_scanner_devices
# async def checkNAPS2installed(): ...
# async def getScannerDevices(type_driver: str = Literal["wia", "twain"]) -> list[str]: ...

from plugin.Scanner.twain_scanner import get_list_scanner_devices


async def checkTWAINinstalled() -> dict[str, bool | str]:
    """Kiểm tra TWAIN bằng cách mở SourceManager và đọc danh sách thiết bị."""
    devices = await get_list_scanner_devices()
    return {
        "installed": bool(devices),
        "message": "TWAIN scanner ready" if devices else "Không tìm thấy thiết bị TWAIN",
    }


async def getScannerDevices() -> list[str]:
    """Lấy tên thiết bị từ TWAIN SourceManager, không phụ thuộc NAPS2."""
    return await get_list_scanner_devices()