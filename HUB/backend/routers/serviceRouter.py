from fastapi import APIRouter, UploadFile, File
from backend.services.serviceServices import getActiveServices, getCategories

service_router = APIRouter(prefix="/services", tags=["services"])

@service_router.get("/active")
async def get_active_services():
    """
    Lấy danh sách các service đang active.
    """
    return getActiveServices()

@service_router.get("/categories")
async def get_categories():
    """
    Lấy danh sách các category của service.
    """
    return getCategories()