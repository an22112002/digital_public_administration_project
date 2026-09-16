from fastapi import APIRouter
from backend.services.settingsServices import get_ui_user, set_ui_user, getCommuneList, getNAPS2Path, getProvinceList, getTitle, setNAPS2Path, setTitle, getProvince, getCommune, savePosition, getMode, saveMode, getSelfIP, getLLMSetting, getLLMModels, setLLMSetting, getLLMServerStatus, unloadLLMModel, loadLLMModel
from backend.models.settingsModels import ModeSaveRequest, SetNAPS2PathRequest, SetPositionRequest, SetTitleRequest, SetLLMSettingRequest, SetUIUserRequest

settings_router = APIRouter(prefix="/settings", tags=["settings"])

# ui người dùng
@settings_router.get("/ui-user")
async def get_ui():
    return await get_ui_user()

@settings_router.put("/ui-user")
async def set_ui(request: SetUIUserRequest):
    return await set_ui_user(request.ui)
# naps2 settings endpoints
@settings_router.get("/naps2-path")
async def get_naps2_path():
    naps2_path = await getNAPS2Path()
    return {"naps2_path": naps2_path}

@settings_router.put("/naps2-path")
async def set_naps2_path(request: SetNAPS2PathRequest):
    result = await setNAPS2Path(request.path)
    if result:
        return {"success": True, "message": "NAPS2 path updated successfully."}
    else:
        return {"success": False, "message": "Failed to update NAPS2 path."}

# user UI settings endpoints
@settings_router.get("/title")
async def get_title():
    title = await getTitle()
    return {"title": title}

@settings_router.put("/title")
async def set_title(request: SetTitleRequest):
    result = await setTitle(request.title)
    if result:
        return {"success": True, "message": "Title updated successfully."}
    else:
        return {"success": False, "message": "Failed to update title."}

# process settings endpoints
@settings_router.get("/province")
async def get_province():
    province = await getProvince()
    return {"province": province}

@settings_router.get("/commune")
async def get_commune():
    commune = await getCommune()
    return {"commune": commune}

@settings_router.get("/province-list")
async def get_province_list():
    # Trả về danh sách các tỉnh/thành phố
    province_list = getProvinceList()
    return province_list

@settings_router.get("/commune-list/{province_id}")
async def get_commune_list(province_id: int):
    # Trả về danh sách các xã/phường thuộc tỉnh/thành phố được chỉ định
    commune_list = getCommuneList(province_id)
    return commune_list

@settings_router.put("/position")
async def set_position(request: SetPositionRequest):
    result = await savePosition(request.provinceID, request.communeID)
    return result

# LLM settings endpoints
@settings_router.get("/llm-models")
async def get_llm_models():
    return await getLLMModels()

@settings_router.get("/llm")
async def get_llm_setting():
    return await getLLMSetting()

@settings_router.get("/llm-server-status")
async def get_llm_status():
    return await getLLMServerStatus()

@settings_router.put("/llm-update")
async def set_llm_setting(request: SetLLMSettingRequest):
    result = await setLLMSetting(
        model=request.model,
        gpu_use=request.gpu_use,
        context_length=request.context_length
    )
    return result

@settings_router.post("/llm-load")
async def load_llm_model():
    result = await loadLLMModel()
    return result

@settings_router.post("/llm-unload")
async def unload_llm_model():
    result = await unloadLLMModel()
    return result

# mode settings endpoints
@settings_router.get("/server-ip")
async def get_server_ip():
    get_mode_result = await getMode()
    if get_mode_result.get("mode") == "client":
        return {"server_ip": get_mode_result.get("server_ip")}
    return {"server_ip": "localhost"}

@settings_router.get("/self-ip")
async def get_self_ip():
    result = getSelfIP()
    return {"self_ip": result}

@settings_router.get("/mode")
async def get_mode():
    # Trả về chế độ hiện tại
    result = await getMode()
    return result

@settings_router.put("/mode")
async def set_mode(request: ModeSaveRequest):
    result = await saveMode(request)
    return result