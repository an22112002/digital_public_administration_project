import json
import traceback
import time
import sys
import base64
import binascii
import uuid

import asyncio
from OCR.main import processOCR2
import cv2

from backend.crud.processCrud import get_service_by_id, get_documents_to_scan, get_service_documents
from backend.models.processModels import UserTask, StartScanRequest, StartWebViewRequest, WebSocketRequest, CropImageRequest, RotateImageRequest
from backend.config import open_settings
from backend.crop.main import splitPDF, detect_and_crop_image, extendImage, crop_with_position

# from PyPDF2 import PdfReader
# from PIL import Image
import os
import pymupdf
from pathlib import Path
# mock:main
from plugin.Scanner.main import ScanStatus, scan_documents_to_folder
from backend.config import open_settings, SCANNER_SAVE_PATH
from backend.utils import remove_accents
from backend.log.main import log_exception

from backend.config import REDIS_HOST, REDIS_PASSWORD, REDIS_PORT
from redis.asyncio import Redis

from plugin.WebView.main import DataProcess

redis_client = Redis(host=REDIS_HOST, password=REDIS_PASSWORD, port=REDIS_PORT, db=0, decode_responses=True)

# Xử lý việc chuẩn hóa tiêu đề tài liệu thêm
def parse_add_document_title(sr_id: str) -> str:
    """
    Chuẩn hóa tiêu đề tài liệu ADD từ srID.
    Hỗ trợ các dạng:
    - ADD:Tên tài liệu
    - ADD:Tên tài liệu:1724669999 (timestamp để định danh tạm phía UI)
    """
    if not sr_id.startswith("ADD:"):
        return sr_id

    raw_title = sr_id[4:]
    parts = raw_title.rsplit(":", 1)

    if len(parts) == 2 and parts[1].isdigit():
        return parts[0].strip()

    return raw_title.strip()

# Xử lý việc bắt đầu quá trình, cung cấp danh sách tài liệu cần quét cho client
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

# Kích hoạt quét tài liệu từ máy scan, lưu file PDF vào thư mục tạm, chia file PDF thành các trang ảnh riêng lẻ và gửi về client
async def scanActivate(data: StartScanRequest, user_task: UserTask):
    # Force stdout/stderr to UTF-8
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(
            encoding="utf-8",
            errors="replace"
        )

    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(
            encoding="utf-8",
            errors="replace"
        )
    try:
        settings = await open_settings()  # Mở cài đặt từ file config

        path_to_naps2 = settings.get("settings", {}).get("naps2_path", "")
        output_folder = SCANNER_SAVE_PATH
        device_name = data.scanner 
        driver = data.driver
        color_mode = "color"
        filename = f"scan_{int(time.time())}"

        scan_status, error_message = await scan_documents_to_folder(
            timestamp=user_task.timestamp,
            path_to_naps2=path_to_naps2,
            output_folder=output_folder,
            filename=filename,
            device_name=device_name,
            driver=driver,
            color_mode=color_mode
        )

        if scan_status == ScanStatus.SUCCESS:
            # đọc file PDF vừa được tạo ra và chia nó ra thành các ảnh JPG
            pdf_path = os.path.join(output_folder, f"patch_{user_task.timestamp}", f"{filename}.pdf")

            output_folder_for_images = os.path.join(output_folder, f"patch_{user_task.timestamp}", "images")
            os.makedirs(output_folder_for_images, exist_ok=True)
            
            begin_int = await count_images_in_folder(output_folder_for_images)

            # chia PDF thành các trang ảnh riêng lẻ
            await splitPDF(pdf_path, begin_int, output_folder_for_images)

            # lấy danh sách các ảnh vừa được tạo ra và gửi về client
            images_paths = await get_images_from_folder(user_task.timestamp, output_folder_for_images)

            await user_task.websocket.send_json({
                "type": "scan_status",
                "status": "success",
                "images": images_paths
            })
        else:
            await user_task.websocket.send_json({
                "type": "scan_status",
                "status": "error",
                "message": error_message
            })
    except Exception as e:
        log_exception(e, "HUB")
        await user_task.websocket.send_json({
            "type": "scan_status",
            "status": "error",
            "message": str(e)
        })

# Xử lý 1 file cụ thể được người dùng yêu cầu crop, nhận vào đường dẫn file ảnh, trả về đường dẫn các file ảnh đã crop
async def processCropImage(request: CropImageRequest, user_task: UserTask):
    if request.position is not None and len(request.position) == 4:
        try:
            cropped_paths = await crop_with_position(request.image, request.position)
            await user_task.websocket.send_json({
                "type": "crop_status",
                "status": "success",
                "cropped_images": cropped_paths
            })
        except Exception as e:
            log_exception(e, "HUB")
            await user_task.websocket.send_json({
                "type": "crop_status",
                "status": "error",
                "message": str(e)
            })
    else:
        try:
            cropped_paths = await detect_and_crop_image(request.image)
            await user_task.websocket.send_json({
                "type": "crop_status",
                "status": "success",
                "cropped_images": cropped_paths
            })
        except Exception as e:
            log_exception(e, "HUB")
            await user_task.websocket.send_json({
                "type": "crop_status",
                "status": "error",
                "message": str(e)
            })

# Xử lý việc xoay ảnh theo góc người dùng yêu cầu, nhận vào đường dẫn file ảnh và góc xoay, trả về đường dẫn file ảnh đã xoay
async def processRotateImage(request: RotateImageRequest, user_task: UserTask):
    try:
        image_path = request.image

        img = cv2.imread(image_path)

        # Xoay 90 độ theo chiều kim đồng hồ
        rotated = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)

        cv2.imwrite(image_path, rotated)

        print(f"[WebSocket] Rotated image saved at: {image_path}")
        print(f"[WebSocket] Sending rotated image path back to client.")
        print(f"[WebSocket] Sent rotated image path back to client: {image_path}")

        await user_task.websocket.send_json({
            "type": "rotate_status",
            "status": "success",
            "rotated_image": image_path
        })
    except Exception as e:
        log_exception(e, "HUB")
        await user_task.websocket.send_json({
            "type": "rotate_status",
            "status": "error",
            "message": str(e)
        })

# Xử lý việc nhập file pdf từ client, chia nó ra thành các trang ảnh và gửi về client
async def processImportFile(data, user_task: UserTask):
    # Force stdout/stderr to UTF-8
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(
            encoding="utf-8",
            errors="replace"
        )

    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(
            encoding="utf-8",
            errors="replace"
        )
    try:
        filename = Path(data.filename).name
        if Path(filename).suffix.lower() != ".pdf":
            raise ValueError("Chỉ chấp nhận file PDF.")

        encoded_file = data.file
        if encoded_file.startswith("data:"):
            header, separator, encoded_file = encoded_file.partition(",")
            if not separator or ";base64" not in header.lower():
                raise ValueError("Nội dung file không hợp lệ.")

        try:
            pdf_bytes = base64.b64decode(encoded_file, validate=True)
        except (binascii.Error, ValueError) as exc:
            raise ValueError("Nội dung file không hợp lệ.") from exc

        if not pdf_bytes.startswith(b"%PDF"):
            raise ValueError("File được chọn không phải PDF hợp lệ.")

        patch_folder = Path(SCANNER_SAVE_PATH) / f"patch_{user_task.timestamp}"
        images_folder = patch_folder / "images"
        patch_folder.mkdir(parents=True, exist_ok=True)
        images_folder.mkdir(parents=True, exist_ok=True)

        imported_pdf_path = patch_folder / f"import_{uuid.uuid4().hex}.pdf"
        imported_pdf_path.write_bytes(pdf_bytes)

        try:
            with pymupdf.open(str(imported_pdf_path)) as pdf:
                if pdf.page_count == 0:
                    raise ValueError("File PDF không có trang.")
        except ValueError:
            imported_pdf_path.unlink(missing_ok=True)
            raise
        except Exception as exc:
            imported_pdf_path.unlink(missing_ok=True)
            raise ValueError("File được chọn không phải PDF hợp lệ.") from exc

        begin_int = await count_images_in_folder(str(images_folder))
        await splitPDF(str(imported_pdf_path), begin_int, str(images_folder))
        images_paths = await get_images_from_folder(user_task.timestamp, str(images_folder))

        await user_task.websocket.send_json({
            "type": "scan_status",
            "status": "success",
            "images": images_paths
        })
    except Exception as exc:
        log_exception(exc, "HUB")
        await user_task.websocket.send_json({
            "type": "scan_status",
            "status": "error",
            "message": str(exc)
        })

# Xử lý các yêu cầu từ WebSocket
async def processWebSocket(data, user_task: UserTask) -> bool:
    request = WebSocketRequest(**data)
    print(f"[WebSocket] Received request: {request.type}")
    if request.type == "start_scan":
        # Xử lý yêu cầu quét tài liệu
        asyncio.create_task(scanActivate(request.request, user_task))
        await user_task.websocket.send_json({
            "type": "scan_status",
            "status": "started"
        })
        return True
    elif request.type == "import_file":
        # Xử lý yêu cầu nhập file
        asyncio.create_task(processImportFile(request.request, user_task))
        await user_task.websocket.send_json({
            "type": "import_file",
            "status": "file import started"
        })
        return True
    elif request.type == "start_webview":
        # Xử lý yêu cầu xem web
        asyncio.create_task(processWebView(request.request, user_task))
        await user_task.websocket.send_json({
            "type": "webview",
            "status": "start data processing"
        })
        return True
    elif request.type == "crop_image":
        # Xử lý yêu cầu crop ảnh
        asyncio.create_task(processCropImage(request.request, user_task))
        await user_task.websocket.send_json({
            "type": "crop_status",
            "status": "crop started"
        })
        return True
    elif request.type == "rotate_image":
        # Xử lý yêu cầu xoay ảnh
        print(f"[WebSocket] Received rotate_image request: {request.request}")
        asyncio.create_task(processRotateImage(request.request, user_task))
        await user_task.websocket.send_json({
            "type": "rotate_status",
            "status": "rotate started"
        })
        return True
    elif request.type == "close":
        await user_task.websocket.close()
        return False

# Chuẩn bị dữ liệu cho webview
async def readyDataForWebView(webview_request: StartWebViewRequest, user_task: UserTask):
    # chuẩn bị dữ liệu cho webview
    # ghép dữ liệu từ service, documents và webview_request thành một cấu trúc dữ liệu phù hợp, thêm các trường từ 
    documents_data = []
    ocr_data = []
    provieded_documents = webview_request.files
    # thiếu tài liệu -> báo lỗi, thừa tài liệu -> thêm vào theo mẫu, đủ tài liệu -> tiếp tục
    required_document_ids = {str(doc["srID"]) for doc in user_task.required_documents}

    for doc in user_task.required_documents:
        # Tài liệu trong user_task là danh sách chuẩn để đối chiếu request.
        matching_doc = next(
            (item for item in provieded_documents if str(item.srID) == str(doc["srID"])),
            None,
        )
        files = matching_doc.files if matching_doc else []
        requirement_type = doc["requirementType"]

        documents_data.append({
            "srID": str(doc["srID"]),
            "title": doc["title"],
            "requirementType": requirement_type,
            "files": files,
            "ocr_enabled": doc["ocr_enabled"],
            "code": doc["code"]
        })
    # thêm các tài liệu thừa vào documents_data
    for prov_doc in provieded_documents:
        if str(prov_doc.srID).startswith("ADD") and str(prov_doc.srID) not in required_document_ids:
            documents_data.append({
                "srID": str(prov_doc.srID),
                "title": parse_add_document_title(str(prov_doc.srID)),
                "requirementType": "OPTIONAL",
                "files": prov_doc.files,
                "ocr_enabled": False,
                "code": await codeForAddDocument(str(prov_doc.srID))
            })
    # REQUIRED và OCR_REQUIREMENT phải xuất hiện và phải có file.
    # CONDITIONAL và OCR_REQUIRED_CONDITIONAL không bắt buộc xuất hiện,
    # nhưng nếu xuất hiện thì phải có file.
    for doc in documents_data:
        requirement_type = doc["requirementType"]
        has_files = bool(doc["files"])
        matching_doc_exists = doc["srID"] in {
            str(item.srID) for item in provieded_documents
        }

        if requirement_type in ["REQUIRED", "OCR_REQUIREMENT"] and not has_files:
            await user_task.websocket.send_json({
                "type": "webview_data",
                "status": "error",
                "message": f"Tài liệu bắt buộc: {doc['title']}, chưa được cung cấp hoặc chưa có file."
            })
            raise ValueError(f"Tài liệu bắt buộc: {doc['title']}, chưa được cung cấp hoặc chưa có file.")

        if (
            requirement_type in ["CONDITIONAL", "OCR_REQUIRED_CONDITIONAL"]
            and matching_doc_exists
            and not has_files
        ):
            await user_task.websocket.send_json({
                "type": "webview_data",
                "status": "error",
                "message": f"Tài liệu đã chọn: {doc['title']}, chưa có file."
            })
            raise ValueError(f"Tài liệu đã chọn: {doc['title']}, chưa có file.")
    # mở rộng ảnh với các tài liệu có yêu cầu
    for doc in documents_data:
        await autoExtendImage(doc)

    # tạo các file PDF từ các file JPG ứng với mỗi tài liệu
    for doc in documents_data:
        if len(doc['files']) > 0:
            output_pdf_path = os.path.join(SCANNER_SAVE_PATH, f"patch_{user_task.timestamp}", "upload", f"{remove_accents(doc['title'])}.pdf")
            upload_folder = Path(SCANNER_SAVE_PATH, f"patch_{user_task.timestamp}", "upload")
            upload_folder.mkdir(parents=True, exist_ok=True)
            await merge_images_to_pdf(doc['files'], output_pdf_path)
            doc['pdf_path'] = output_pdf_path
        else:
            doc['pdf_path'] = ""
    # xử lý các tài liệu cần ocr
    # nếu mode = basic thì bỏ qua ocr, nếu ko thì thực hiện ocr cho các tài liệu cần ocr
    if user_task.mode == "basic":
        ocr_final_results = []
        for doc in documents_data:
            if doc['ocr_enabled']:
                doc['ocr_enabled'] = False
    else:
        server_ip = user_task.server_ip
        for doc in documents_data:
            if doc['ocr_enabled'] and len(doc['files']) > 0:
                ocr_data.append({
                    "srID": doc['srID'],
                    "code": doc['code'],
                    "files": doc['files']
                })
        ocr_final_results = await OCRDocuments(ocr_data, server_ip)
    # lấy danh sách tài liệu cần upload: service_documents của service
    service_docs = get_service_documents(user_task.service['serviceID'])
    for doc in service_docs:
        doc['ready'] = False

    # chuẩn bị dữ liệu cho webview
    settings = await open_settings()  # Mở cài đặt từ file config
    data_process = []
    data_auto_pass = {
        "province": settings.get("settings", {}).get("province", "Unknown"),
        "commune": settings.get("settings", {}).get("commune", "Unknown"),
        "button_send_documents_position": user_task.service.get("buttonPosition", 1),
    }
    data_process.append(DataProcess(task_name="auto_pass_select_service", data=data_auto_pass))

    files_insert_data = []
    # thêm các tài liệu bổ sung vào files_insert_data
    for doc in documents_data:
        if doc["srID"].startswith("ADD"):
            files_insert_data.append({
                "name": doc['title'],
                "file": doc['pdf_path'],
                "ref": doc['srID']
            })
    # xử lý doc SCAN
    for doc in service_docs:
        source_type = doc["sourceType"]
        source_ref = doc["sourceRef"]
        # nếu source_type là "SCAN" thì tìm tài liệu tương ứng trong documents_data theo source_ref (là code của tài liệu), nếu tìm thấy thì thêm vào files_insert_data
        if source_type == "SCAN":
            source_refs = [ref.strip() for ref in (source_ref or "").split("|") if ref.strip()]
            normalized_source_ref = str(source_ref or "").strip()
            matching_doc = next(
                (
                    d for d in documents_data
                    if str(d.get("code") or "").strip() == normalized_source_ref
                ),
                None,
            )
            # nếu match -> tài liệu kiểu thường
            if matching_doc and matching_doc["files"]:
                files_insert_data.append({
                    "name": doc['realTitle'],
                    "file": matching_doc['pdf_path'],
                    "ref": doc['sourceRef']
                })
                doc['ready'] = True
            # nếu không match -> tài liệu kiểu đặc biệt, kết hơp từ nhiều tài liệu, ví dụ: "CCCD vợ chồng" -> ghép từ "CCCD chồng" và "CCCD vợ"
            else:
                images_to_merge = []
                all_refs_available = bool(source_refs)
                missing_refs = []
                for sr in source_refs:
                    matching_doc = next(
                        (
                            d for d in documents_data
                            if str(d.get("code") or "").strip() == sr
                        ),
                        None,
                    )
                    if matching_doc and matching_doc["files"]:
                        images_to_merge.extend(matching_doc['files'])
                    else:
                        all_refs_available = False
                        missing_refs.append(sr)
                if all_refs_available and images_to_merge:
                    os.makedirs(os.path.join(SCANNER_SAVE_PATH, f"patch_{user_task.timestamp}", "upload"), exist_ok=True)
                    output_pdf_path = os.path.join(SCANNER_SAVE_PATH, f"patch_{user_task.timestamp}", "upload", f"Giay_to_{doc['sdID']}.pdf")
                    await merge_images_to_pdf(images_to_merge, output_pdf_path)
                    files_insert_data.append({
                        "name": doc['realTitle'],
                        "file": output_pdf_path,
                        "ref": doc['sourceRef']
                    })
                    doc['ready'] = True
                elif missing_refs:
                    doc["skip_webview"] = True
                    print(
                        f"missing files for refs: {', '.join(missing_refs)}"
                    )
    # xử lý doc FORM
    for doc in service_docs:
        source_type = doc["sourceType"]
        source_ref = doc["sourceRef"]          
        if source_type == "FORM":
            if user_task.mode == "basic":
                # nếu mode = basic thì bỏ qua ocr, đánh dấu tất cả các doc FORM là ready
                doc['ready'] = True
                continue
            form_key = doc["formKey"]
            source_refs = source_ref.split("|")
            # số lượng tài liệu cần ocr, bỏ qua các tài liệu đặc biệt có @
            # tài liệu có @, là tài liệu đặc biệt, có thể có hoặc ko cần ocr, ví dụ: "Giấy tờ bổ sung" -> có thể có hoặc ko cần ocr
            min_refs = len([sr for sr in source_refs if "@" not in sr])
            max_refs = len(source_refs)  
            OCRDocsRequested = []
            # xử lý các tài liệu cần nhập form, data lấy từ ocr
            for sr in source_refs:
                if sr.startswith("ocr_"):
                    key = sr[4:]
                else:
                    key = sr
                key = key.replace("@", "")
                for ocr_data in ocr_final_results:
                    if key == ocr_data['type']:
                        OCRDocsRequested.append(ocr_data)
            # số lượng tài liệu đã OCR phải nằm trong khoảng từ số lượng tài liệu tối thiểu đến số lượng tài liệu tối đa, nếu ko thì báo lỗi
            print(OCRDocsRequested)
            if min_refs <= len(OCRDocsRequested) <= max_refs:
                OCRDocsRequested = await processLogicOCRData(form_key, OCRDocsRequested, files_insert_data)
                # nếu đủ số lượng tài liệu cần ocr thì ok
                data_process.append(DataProcess(task_name=form_key, data=OCRDocsRequested))
                doc['ready'] = True
            else:
                await user_task.websocket.send_json({
                    "type": "webview_data",
                    "status": "error",
                    "message": f"Tài liệu cần ocr: {doc['realTitle']}, số lượng tài liệu ocr không đủ. Yêu cầu từ {min_refs} đến {max_refs}, nhưng chỉ nhận được {len(OCRDocsRequested)}."
                })
                raise ValueError(f"Tài liệu cần ocr: {doc['realTitle']}, số lượng tài liệu ocr không đủ. Yêu cầu từ {min_refs} đến {max_refs}, nhưng chỉ nhận được {len(OCRDocsRequested)}.")
    # kiểm tra xem tất cả các tài liệu cần upload đã sẵn sàng chưa, nếu chưa thì gửi thông báo lỗi
    for doc in service_docs:
        if doc.get("skip_webview"):
            continue
        if not doc['ready']:
            await user_task.websocket.send_json({
                "type": "webview_data",
                "status": "error",
                "message": f"Tài liệu cần upload: {doc['realTitle']}, chưa sẵn sàng."
            })
            raise ValueError("Tài liệu cần upload chưa sẵn sàng.")
    # nếu tất cả các tài liệu đã sẵn sàng, gửi dữ liệu về webview
    data_process.append(DataProcess(task_name="insert_file_table", data=files_insert_data))
    # for dp in data_process:
    #     dp.print_out()
    return data_process

# process webview
async def processWebView(webview_request: StartWebViewRequest, user_task: UserTask):

    # Force stdout/stderr to UTF-8
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(
            encoding="utf-8",
            errors="replace"
        )

    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(
            encoding="utf-8",
            errors="replace"
        )

    try:
        user_task.set_data_from_client(webview_request)
        if not user_task.is_ready_for_web_view():
            user_task.data_ready_for_web_view = await readyDataForWebView(webview_request, user_task)
            user_task.need_process = False
        # gửi redis để worker webview nhận và xử lý
        await redis_client.rpush(
            "webview",
            json.dumps({
                "start": True,
                "data": {
                    "url": user_task.url,
                    "data_process": [
                        dp.to_dict()
                        for dp in user_task.data_ready_for_web_view
                    ]
                }
            }, ensure_ascii=False)
        )

        await user_task.websocket.send_json({
            "type": "webview",
            "status": "started"
        })
    except ValueError as ve:
        print(f"ValueError in processWebView: {ve}")
        await user_task.websocket.send_json({
            "type": "webview",
            "status": "error",
            "message": str(ve)
        })
    except Exception as e:
        print(f"Error in processWebView: {e}")
        log_exception(e, "HUB")
        traceback.print_exc()
        try:
            await user_task.websocket.send_json({
                "type": "webview",
                "status": "error",
                "message": str(e)
            })
        except Exception as send_error:
            log_exception(send_error, "HUB")
            pass

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

# mở rộng ảnh theo chiều dài và chiều rộng, phần mở rộng là các pixel trắng (255,255,255), rồi lưu lại ảnh mới và trả về đường dẫn mới
async def autoExtendImage(document: list[dict]):
    # kiểm tra xem tài liệu có cần mở rộng hay không, nếu có thì mở rộng ảnh theo các thông số đã định nghĩa sẵn
    filter = [
        {"code": "cccd", "ex_x": 0.15, "ex_y": 0.25},
        {"code": "gplx", "ex_x": 0.15, "ex_y": 0.25},
        {"code": "bhyt", "ex_x": 0.15, "ex_y": 0.25},
    ]
    is_extendable = False
    ex_x = 0
    ex_y = 0
    # kiểm tra xem có tài liệu nào cần mở rộng hay không
    for f in filter:
        if document["code"].startswith(f["code"]):
            is_extendable = True
            ex_x = f["ex_x"]
            ex_y = f["ex_y"]
            break
    # nếu có tài liệu cần mở rộng thì thực hiện mở rộng ảnh
    if is_extendable:
        if len(document['files']) > 0:
            extended_files = []
            for image_path in document['files']:
                extended_image_path = await extendImage(ex_x, ex_y, image_path)
                extended_files.append(extended_image_path)
            document['files'] = extended_files

# chia PDF thành các trang riêng lẻ, mỗi trang là một file JPG mới
# crop các ảnh tài liệu nhỏ về kích thước của chúng
# async def splitPDF(pdf_path: str, begin_int: int, output_folder: str):
#     output_path = Path(output_folder)
#     output_path.mkdir(parents=True, exist_ok=True)

#     pdf = pymupdf.open(pdf_path)

#     try:
#         for i, page in enumerate(pdf):
#             pix = page.get_pixmap(dpi=300)

#             image_path = output_path / f"page_{i + begin_int}.jpg"

#             pix.save(str(image_path))

#     finally:
#         pdf.close()

# đếm số ảnh trong một folder
async def count_images_in_folder(folder_path: str):
    count = 0
    for file_name in os.listdir(folder_path):
        if file_name.lower().endswith(('.png', '.jpg', '.jpeg')):
            count += 1
    return count

# lấy danh sách ảnh từ folder
async def get_images_from_folder(timestamp: int, folder_path: str):
    images = []
    for file_name in os.listdir(folder_path):
        if file_name.lower().endswith(('.png', '.jpg', '.jpeg')):
            images.append({
                "url": os.path.join(folder_path, file_name),
                "link": f"/scanned-files/patch_{timestamp}/images/{file_name}"
            })
    return images

async def codeForAddDocument(srID: str):
    """
    Hàm chuẩn hóa mã code cho các tài liệu bổ sung (ADD).
    :param srID: str - ID của yêu cầu quét, nếu là "ADD:<tên tài liệu>" thì nó là tài liệu bổ sung
    :return: str - mã code chuẩn hóa cho tài liệu bổ sung."""
    if not srID.startswith("ADD:"):
        raise ValueError(f"srID không hợp lệ: {srID}")
    raw_title = srID[4:]
    parts = raw_title.rsplit(":", 1)
    if len(parts) == 2 and parts[1].isdigit():
        title = parts[0].strip()
    else:
        title = raw_title.strip()
    # chuẩn hóa title thành code, ví dụ: "Giấy khai sinh" -> "giay_khai_sinh"
    s = remove_accents(title).lower().replace(" ", "_")
    code = ""
    if s in ("can_cuoc_cong_dan", "cccd", "can_cuoc", "chung_minh_nhan_dan", "ho_chieu"):
        code = "cccd"
    if s in ("giay_phep_lai_xe", "gplx", "bang_lai_xe"):
        code = "gplx"
    if s in ("giay_bao_hiem_y_te", "bhyt", "bao_hiem_y_te"):
        code = "bhyt"
    return code

async def OCRDocuments(ocr_data: list[dict], server_ip: str):
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
        # thực hiện OCR cho từng document cần OCR
        result = await processOCR2(code, files, server_ip)
        if result is not None:
            ocr_final_results.append(result)
        else:
            raise ValueError(f"Không đọc được thông tin của: {code}")
    # print(f"OCR final results: {ocr_final_results}")
    return ocr_final_results

async def processLogicOCRData(form_key, OCRDocsRequested, files_insert_data):
    """
    Hàm xử lý logic dữ liệu OCR cho các tài liệu cần điền form.
    :param form_key: str - khóa của form cần điền
    :param OCRDocsRequested: list[dict] - danh sách tài liệu cần OCR
    :param files_insert_data: list[dict] - danh sách các file cần điền vào form
    :return: list[dict] - danh sách các dict chứa dữ liệu đã xử lý cho form
    """
    if form_key == "form_xacNhanTinhTrangHonNhan":
        # nếu có ref d6_3 trong files_insert_data của cccd_self thì đánh dấu firstTime = False, nếu không thì firstTime = True
        cccd_do = next((d for d in OCRDocsRequested if d['type'] == 'cccd_do'), None)
        cccd_main = next((d for d in OCRDocsRequested if d['type'] == 'cccd_main'), None)
        if cccd_do:
            cccd_process = cccd_do
        else:
            cccd_process = cccd_main
        x = any(f.get('ref') == 'd6_3' and f.get('file') != "" for f in files_insert_data)
        if x:
            cccd_process["firstTime"] = False
        else:
            cccd_process["firstTime"] = True
        OCRDocsRequested = [d for d in OCRDocsRequested if d['type'] != cccd_process['type']]
        OCRDocsRequested.append(cccd_process)
        
    return OCRDocsRequested

    