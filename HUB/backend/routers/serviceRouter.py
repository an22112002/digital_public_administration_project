from fastapi import APIRouter, HTTPException
from backend.models.serviceModels import SetServiceActiveRequest
from backend.services.serviceServices import getAllServices, getCategories, get_services, setServiceActive

service_router = APIRouter(prefix="/services", tags=["services"])

@service_router.get("/all")
async def get_all_services():
    """
    Lấy toàn bộ danh sách service, bao gồm cả service đang inactive.
    """
    return getAllServices()

@service_router.get("/service-list")
async def get_active_services(category: str | None = None, title: str | None = None):
    """
    Lấy danh sách các service đang active.
    """
    return get_services(category=category, title=title)

@service_router.get("/categories")
async def get_categories():
    """
    Lấy danh sách các category của service.
    """
    return getCategories()

@service_router.put("/{service_id}/active")
async def set_service_active(service_id: int, request: SetServiceActiveRequest):
    """
    Bật hoặc tắt một service theo serviceID.
    """
    updated = setServiceActive(service_id, request.active)
    if not updated:
        raise HTTPException(status_code=404, detail="Service not found")
    return {"success": True, "serviceID": str(service_id), "active": request.active}