from fastapi import APIRouter
from backend.services.settingsServices import getCommuneList, getNAPS2Path, getProvinceList, getTitle, setNAPS2Path, setTitle, getProvince, getCommune, savePosition
from backend.models.settingsModels import SetNAPS2PathRequest, SetPositionRequest, SetTitleRequest

settings_router = APIRouter(prefix="/settings", tags=["settings"])

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