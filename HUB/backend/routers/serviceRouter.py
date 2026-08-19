from fastapi import APIRouter, UploadFile, File

from backend.services.serviceServices import import_xlsx


service_router = APIRouter(prefix="/services", tags=["services"])
