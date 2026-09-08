from backend.config import open_settings, save_settings
from backend.crud.settingsCrud import get_province_list, get_commune_list, get_position
from backend.log.main import log_exception

async def getNAPS2Path() -> str:
    settings_data = await open_settings()
    naps2_path = settings_data.get("settings", {}).get("naps2_path", "Unknown")
    return naps2_path

async def setNAPS2Path(new_path: str) -> bool:
    try:
        settings_data = await open_settings()
        settings_data["settings"]["naps2_path"] = new_path
        await save_settings(settings_data)
        return True
    except Exception as e:
        log_exception(e, "HUB")
        print(f"[Error] Failed to set NAPS2 path: {e}")
        return False

async def getTitle() -> str:
    settings_data = await open_settings()
    title = settings_data.get("settings", {}).get("title", "Unknown")
    return title

async def setTitle(new_title: str) -> bool:
    try:
        settings_data = await open_settings()
        settings_data["settings"]["title"] = new_title
        await save_settings(settings_data)
        return True
    except Exception as e:
        log_exception(e, "HUB")
        print(f"[Error] Failed to set title: {e}")
        return False

async def getProvince() -> str:
    settings_data = await open_settings()
    province = settings_data.get("settings", {}).get("province", "Unknown")
    return province

async def getCommune() -> str:
    settings_data = await open_settings()
    commune = settings_data.get("settings", {}).get("commune", "Unknown")
    return commune

def getProvinceList() -> list:
    data = get_province_list()
    result = [{"name": item["name"], "id": str(item["provinceID"])} for item in data]
    return {"province_list": result}

def getCommuneList(province_id: int) -> list:
    data = get_commune_list(province_id)
    result = [{"name": item["name"], "id": str(item["communeID"])} for item in data]
    return {"commune_list": result}

async def savePosition(province_id: str, commune_id: str):
    try:
        province_id = int(province_id)
        commune_id = int(commune_id)
        province_name, commune_name = get_position(province_id, commune_id)
        if province_name and commune_name:
            settings_data = await open_settings()
            settings_data["settings"]["province"] = province_name
            settings_data["settings"]["commune"] = commune_name
            await save_settings(settings_data)
            return {"success": True, "message": "Đã lưu vị trí thành công."}
        else:
            return {"success": False, "message": "Lỗi không tìm thấy tỉnh/thành phố hoặc xã/phường."}
    except Exception as e:
        log_exception(e, "HUB")
        print(f"[Error] Failed to save position: {e}")
        return {"success": False, "message": "Lỗi khi lưu vị trí.", "error": str(e)}