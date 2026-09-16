from backend.config import open_settings, save_settings
from backend.crud.settingsCrud import get_province_list, get_commune_list, get_position
from backend.log.main import log_exception
from backend.models.settingsModels import ModeSaveRequest
from backend.services.LLMServices import checkLMStudioServerRunning, loadLocalLMStudioModel, unloadLocalLMStudioModel, runPromptInLMStudio
import socket

# NAPS2 settings functions
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

# user UI settings functions
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

# process settings functions
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

# LLM settings functions
async def getLLMModels() -> list:
    # Trả về danh sách các mô hình LLM có sẵn
    return [
        "qwen3-vl-2b-instruct",
        "qwen3-vl-4b-instruct",
        "qwen3-vl-8b-instruct",
    ]

async def getLLMSetting() -> dict:
    settings_data = await open_settings()
    llm_model = settings_data.get("settings").get("LLM_model", "Unknown")
    llm_gpu_use = settings_data.get("settings").get("LLM_gpu_use", 0.0)
    llm_context_length = settings_data.get("settings").get("LLM_context_length", 8192)
    return {
        "LLM_model": llm_model,
        "LLM_gpu_use": llm_gpu_use,
        "LLM_context_length": llm_context_length
    }

async def setLLMSetting(model: str, gpu_use: float, context_length: int) -> bool:
    try:
        if gpu_use < 0.0 or gpu_use > 1.0:
            raise ValueError("Giá trị GPU use phải nằm trong khoảng từ 0.0 đến 1.0.")
        if context_length <= 0:
            raise ValueError("Chiều dài ngữ cảnh phải là một số dương.")
        settings_data = await open_settings()
        settings_data["settings"]["LLM_model"] = model
        settings_data["settings"]["LLM_gpu_use"] = gpu_use
        settings_data["settings"]["LLM_context_length"] = context_length
        await save_settings(settings_data)
        return {"success": True, "message": "Đã lưu cài đặt LLM thành công."}
    except Exception as e:
        log_exception(e, "HUB")
        print(f"[Error] Failed to set LLM settings: {e}")
        return {"success": False, "message": "Lỗi khi lưu cài đặt LLM.", "error": str(e)}

async def getLLMServerStatus() -> bool:
    # Kiểm tra trạng thái của server LLM Studio
    # chỉ hoạt động khi chế độ là "server" nên server_ip = "localhost"
    is_running = await checkLMStudioServerRunning("localhost")
    return {"state": is_running}

async def unloadLLMModel() -> dict:
    await unloadLocalLMStudioModel()
    try:
        _ = await runPromptInLMStudio(prompt="hello", images=[], server_ip="localhost")
        return {"success": False, "message": "Mô hình LLM vẫn đang chạy."}
    except Exception as e:
        return {"success": True, "message": "Đã unload mô hình LLM thành công."}

async def loadLLMModel() -> dict:
    await loadLocalLMStudioModel()
    try:
        _ = await runPromptInLMStudio(prompt="hello", images=[], server_ip="localhost")
        return {"success": True, "message": "Đã load mô hình LLM thành công."}
    except Exception as e:
        return {"success": False, "message": "Mô hình LLM không phản hồi.", "error": str(e)}

# mode settings functions
def getSelfIP() -> str:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    finally:
        s.close()

async def getMode() -> str:
    settings_data = await open_settings()
    mode = settings_data.get("settings", {}).get("mode", "Unknown")
    if mode == "client":
        ip = settings_data.get("settings", {}).get("server_ip", "")
        return {
            "mode": mode,
            "server_ip": ip
        }
    return {
        "mode": mode
    }

async def saveMode(data: ModeSaveRequest) -> dict:
    try:
        settings_data = await open_settings()
        settings_data["settings"]["mode"] = data.mode
        if data.mode == "client":
            settings_data["settings"]["server_ip"] = data.server_ip
        await save_settings(settings_data)
        return {"success": True, "message": "Chế độ đã được lưu thành công."}
    except Exception as e:
        log_exception(e, "HUB")
        print(f"[Error] Failed to save mode: {e}")
        return {"success": False, "message": "Lỗi khi lưu chế độ.", "error": str(e)}