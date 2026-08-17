from fastapi import APIRouter, UploadFile, File

from backend.services.serviceServices import import_xlsx


service_router = APIRouter(prefix="/services", tags=["services"])

@service_router.post("/xlsx")
async def import_xlsx_file(
    file: UploadFile = File(...)
):
    """
    API import dữ liệu từ file XLSX.

    File phải chứa 3 sheet:

    - services
    - default
    - extention
    """

    # Đọc toàn bộ file thành bytes.
    file_data = await file.read()

    # Gọi service xử lý import.
    result = import_xlsx(file_data)
    print(result)

    return {
        "success": True,
        "message": "Import dữ liệu thành công"
    }