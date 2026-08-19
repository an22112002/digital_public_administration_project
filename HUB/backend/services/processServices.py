from fastapi import WebSocket
import asyncio
from OCR.main import OCR_CCCD

from backend.crud.processCrud import get_active_services, get_service_by_id, get_documents_to_scan, get_service_documents
from backend.models.processModels import StartScanRequest, DocumentFile, StartWebViewRequest, WebSocketRequest
from backend.config import open_settings

# from PyPDF2 import PdfReader
# from PIL import Image
import os
import pymupdf
from pathlib import Path

from plugin.Scanner.main import ScanStatus, scan_documents_to_folder
from plugin.WebView.main import DataProcess
from backend.config import open_settings, SCANNER_SAVE_PATH
from backend.utils import remove_accents

def getActiveServices():
    return get_active_services()

def startProcess(service_id: str):
    # kiểm tra xem service có tồn tại không
    service = get_service_by_id(service_id)
    if not service:
        raise ValueError(f"Service with ID {service_id} does not exist.")
    # kiểm tra xem service có đang hoạt động không
    if not service['active']:
        raise RuntimeError(f"Service with ID {service_id} is not active.")
    # Lấy danh sách tài liệu cần quét cho service
    documents = get_documents_to_scan(service_id)
    # trả về dữ liệu
    return service, documents

async def scanActivate(timestamp: int, data: StartScanRequest, websocket: WebSocket):
    try:
        settings = await open_settings()  # Mở cài đặt từ file config

        path_to_naps2 = settings.get("path_to_naps2", "")
        output_folder = SCANNER_SAVE_PATH
        device_name = data.scanner 
        driver = data.driver
        color_mode = "color"

        scan_status, error_message = await scan_documents_to_folder(
            timestamp=timestamp,
            path_to_naps2=path_to_naps2,
            output_folder=output_folder,
            device_name=device_name,
            driver=driver,
            color_mode=color_mode
        )

        if scan_status == ScanStatus.SUCCESS:
            # đọc file PDF vừa được tạo ra và chia nó ra thành các ảnh JPG
            pdf_path = os.path.join(output_folder, f"patch_{timestamp}", "scan.pdf")
            output_folder_for_images = os.path.join(output_folder, f"patch_{timestamp}", "images")
            images_paths = await splitPDF(pdf_path, output_folder_for_images)

            await websocket.send_json({
                "type": "scan_status",
                "status": "success",
                "images": images_paths
            })
        else:
            await websocket.send_json({
                "type": "scan_status",
                "status": "error",
                "message": error_message
            })
    except Exception as e:
        await websocket.send_json({
            "type": "scan_status",
            "status": "error",
            "message": str(e)
        })

async def processWebSocket(data, service: dict, required_documents: list, timestamp: int, websocket: WebSocket) -> bool:
    request = WebSocketRequest(**data)
    if request.type == "start_scan":
        asyncio.create_task(scanActivate(timestamp, request.request, websocket))
        await websocket.send_json({
            "type": "scan_status",
            "status": "started"
        })
        return True
    elif request.type == "start_webview":
        # Xử lý yêu cầu xem web
        asyncio.create_task(readyDataForWebView(timestamp, service, required_documents, request.request, websocket))
        await websocket.send_json({
            "type": "webview_data",
            "status": "ready documents"
        })
        return True
    elif request.type == "close":
        await websocket.close()
        return False

async def readyDataForWebView(timestamp: int, service: dict, required_documents: list, webview_request: StartWebViewRequest, websocket: WebSocket):
    # chuẩn bị dữ liệu cho webview
    # ghép dữ liệu từ service, documents và webview_request thành một cấu trúc dữ liệu phù hợp, thêm các trường từ 
    documents_data = []
    ocr_data = []
    provieded_documents = webview_request.files
    # thiếu tài liệu -> báo lỗi, thừa tài liệu -> thêm vào theo mẫu, đủ tài liệu -> tiếp tục
    for doc in required_documents:
        # tìm tài liệu tương ứng trong provieded_documents
        matching_doc = next((d for d in provieded_documents if d.srID == doc['srID']), None)
        if matching_doc:
            documents_data.append({
                "srID": doc['srID'],
                "title": doc['title'],
                "required": doc['required'],
                "files": matching_doc.files,
                "ocr_enabled": doc['ocr_enabled'],
                "code": doc['code']
            })
    # 
    if len(documents_data) < len(required_documents):
        await websocket.send_json({
            "type": "webview_data",
            "status": "error",
            "message": "Thiếu tài liệu cần thiết."
        })
        return
    # thêm các tài liệu thừa vào documents_data
    for prov_doc in provieded_documents:
        if prov_doc.srID.startswith("ADD"):
            documents_data.append({
                "srID": prov_doc.srID,
                "title": prov_doc.srID[4:],  # lấy tên tài liệu từ srID, ví dụ "ADD:Giấy tờ bổ sung" -> "Giấy tờ bổ sung"
                "required": False,
                "files": prov_doc.files,
                "ocr_enabled": False,
                "code": ""
            })
    # Kiểm tra các tài liệu required có len(files) > 0 hay không, nếu không thì gửi thông báo lỗi
    for doc in documents_data:
        if doc['required'] and not doc['files']:
            await websocket.send_json({
                "type": "webview_data",
                "status": "error",
                "message": f"Tài liệu bắt buộc: {doc['title']}, chưa được cung cấp."
            })
            return
    # tạo các file PDF từ các file JPG ứng với mỗi tài liệu
    for doc in documents_data:
        if doc['files']:
            output_pdf_path = os.path.join(SCANNER_SAVE_PATH, f"patch_{timestamp}", "upload", f"{remove_accents(doc['title'])}.pdf")
            await merge_images_to_pdf(doc['files'], output_pdf_path)
            doc['pdf_path'] = output_pdf_path
    # xử lý các tài liệu cần ocr
    for doc in documents_data:
        if doc['ocr_enabled']:
            ocr_data.append({
                "srID": doc['srID'],
                "code": doc['code'],
                "files": doc['files']
            })
    ocr_final_results = await OCRDocuments(ocr_data)
    # lấy danh sách tài liệu cần upload: service_documents của service
    service_docs = get_service_documents(service['serviceID'])
    for doc in service_docs:
        doc['ready'] = False

    # chuẩn bị dữ liệu cho webview
    settings = await open_settings()  # Mở cài đặt từ file config

    url = service['url']
    data_process = []
    data_auto_pass = {
        "province": settings.get("province", ""),
        "commune": settings.get("commune", ""),
        "button_send_documents_position": 1
    }

    files_insert_data = []
    # thêm các tài liệu bổ sung vào files_insert_data
    for doc in documents_data:
        if doc["srID"].startswith("ADD"):
            files_insert_data.append({
                "name": doc['title'],
                "file": doc['pdf_path']
            })
    for doc in service_docs:
        source_type = doc["sourceType"]
        source_ref = doc["sourceRef"]
        # nếu source_type là "SCAN" thì tìm tài liệu tương ứng trong documents_data theo source_ref (là code của tài liệu), nếu tìm thấy thì thêm vào files_insert_data
        if source_type == "SCAN":
            matching_doc = next((d for d in documents_data if d['code'] == source_ref), None)
            # nếu match -> tài liệu kiểu thường
            if matching_doc:
                files_insert_data.append({
                    "name": doc['realTitle'],
                    "file": matching_doc['pdf_path']
                })
                doc['ready'] = True
            # nếu không match -> tài liệu kiểu đặc biệt, kết hơp từ nhiều tài liệu, ví dụ: "CCCD vợ chồng" -> ghép từ "CCCD chồng" và "CCCD vợ"
            else:
                # tìm các source_ref
                source_refs = source_ref.split("|")
                images_to_merge = []
                for sr in source_refs:
                    matching_doc = next((d for d in documents_data if d['code'] == sr), None)
                    if matching_doc:
                        images_to_merge.extend(matching_doc['files'])
                if images_to_merge:
                    output_pdf_path = os.path.join(SCANNER_SAVE_PATH, f"patch_{timestamp}", "upload", f"Giay_to_{doc['sdID']}.pdf")
                    await merge_images_to_pdf(images_to_merge, output_pdf_path)
                    files_insert_data.append({
                        "name": doc['realTitle'],
                        "file": output_pdf_path
                    })
                    doc['ready'] = True
        elif source_type == "FORM":
            form_key = doc["formKey"]
            source_refs = source_ref.split("|")
            OCRDocsRequested = []
            # xử lý các tài liệu cần nhập form, data lấy từ ocr
            for sr in source_refs:
                for ocr_data in ocr_final_results:
                    if sr.remove("ocr_") == ocr_data['type']:
                        OCRDocsRequested.append(ocr_data)
            if len(OCRDocsRequested) == len(source_refs):
                # nếu đủ số lượng tài liệu cần ocr thì ok
                data_process.append(
                    DataProcess(
                        task_name=form_key, 
                        data=OCRDocsRequested
                        )
                    )
                doc['ready'] = True
    # kiểm tra xem tất cả các tài liệu cần upload đã sẵn sàng chưa, nếu chưa thì gửi thông báo lỗi
    for doc in service_docs:
        if not doc['ready']:
            await websocket.send_json({
                "type": "webview_data",
                "status": "error",
                "message": f"Tài liệu cần upload: {doc['realTitle']}, chưa sẵn sàng."
            })
    # nếu tất cả các tài liệu đã sẵn sàng, gửi dữ liệu về webview
    data_process.append(DataProcess(task_name="auto_pass_select_service", data=data_auto_pass))
    data_process.append(DataProcess(task_name="insert_file_table", data=files_insert_data))
    return url, data_process
        

# nối các file JPG thành một file PDF ứng với mỗi tài liệu
async def merge_images_to_pdf(images: list[str], output_pdf_path: str):
    pdf = pymupdf.open()
    for image_path in images:
        img = pymupdf.open(image_path)
        rect = img[0].rect
        pdf_page = pdf.new_page(width=rect.width, height=rect.height)
        pdf_page.insert_image(rect, filename=image_path)
        img.close()
    pdf.save(output_pdf_path)
    pdf.close()

# chia PDF thành các trang riêng lẻ, mỗi trang là một file JPG mới
async def splitPDF(pdf_path: str, output_folder: str):
    output_path = Path(output_folder)
    output_path.mkdir(parents=True, exist_ok=True)

    pdf = pymupdf.open(pdf_path)

    images_path = []

    try:
        for i, page in enumerate(pdf):
            pix = page.get_pixmap(dpi=300)

            image_path = output_path / f"page_{i + 1}.jpg"

            pix.save(str(image_path))

            images_path.append(str(image_path))

    finally:
        pdf.close()
    return images_path

async def OCRDocuments(ocr_data: list[dict]):
    """
    Hàm thực hiện OCR cho các tài liệu trong ocr_data.
    :param ocr_data: Danh sách các dict, mỗi dict có 
    srID: str - ID của yêu cầu quét, nếu là "ADD:<tên tài liệu>" thì nó là tài liệu bổ sung
    code: str - mã của tài liệu, ví dụ: "cccd_huband", "cccd_wife"
    files: list[str] - danh sách đường dẫn đến các file cần OCR
    :return: Danh sách các dict chứa kết quả OCR."""
    # xử lý OCR cho các tài liệu trong ocr_data
    # ocr_data là một danh sách các dict, mỗi dict có srID và files
    ocr_final_results = []
    for doc in ocr_data:
        code = doc['code']
        files = doc['files']
        # thực hiện OCR cho từng file trong files
        ocr_results = []
        for file in files:
            ocr_result = await processOCR(code, file)
            if ocr_result:
                ocr_results.append(ocr_result)
        if len(ocr_results) > 0:
            ocr_final_results.append(
                ocr_results[0]  # chỉ lấy kết quả OCR đầu tiên, nếu có nhiều file thì chỉ lấy kết quả của file đầu tiên
            )
    return ocr_final_results

async def processOCR(code: str, path_to_file: str):
    if code == "cccd_huband":
        result = await OCR_CCCD(path_to_file)
        if result:
            result["type"] = "cccd_huband"
            return result
        return None
    if code == "cccd_wife":
        result = await OCR_CCCD(path_to_file)
        if result:
            result["type"] = "cccd_wife"
            return result
        return None
    # mở rộng cho các loại tài liệu khác nếu cần
    return None
    