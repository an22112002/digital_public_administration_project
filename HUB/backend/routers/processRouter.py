import time

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from backend.services.processServices import processWebSocket, startProcess

from backend.models.processModels import StartProcessResponse

process_router = APIRouter(prefix="/process", tags=["process"])


# ----------------------------------
from backend.config import REDIS_HOST, REDIS_PASSWORD, REDIS_PORT
from redis.asyncio import Redis
from plugin.WebView.main import DataProcess
import json

redis_client = Redis(host=REDIS_HOST, password=REDIS_PASSWORD, port=REDIS_PORT, db=0, decode_responses=True)
#----------------------------------

@process_router.websocket("/test")
async def test_websocket(websocket: WebSocket):
    await websocket.accept()
    try:
        url = (
            "https://dichvucong.gov.vn/"
            "tim-kiem-thu-tuc-hanh-chinh"
            "?formalityId=019d2bfd-95fa-70ca-93fd-4cab11b87897"
            "&formalityCaseId=019db06b-1e13-773f-bd01-af4904294075"
        )

        province = "Thành phố Hà Nội"
        commune = "Phường Ba Đình"

        data_auto_pass = {
            "province": province,
            "commune": commune,
            "button_send_documents_position": 1
        }

        paper_input = [
            {
                "name": "Giấy tờ 1",
                "file": r"D:\test\test.pdf"
            },
            {
                "name": "Dự thảo giao dịch",
                "file": r"D:\test\test2.pdf"
            },
            {
                "name": "CCCD",
                "file": r"D:\test\test3.pdf"
            },
        ]

        data_process = [
            DataProcess(
                task_name="auto_pass_select_service",
                data=data_auto_pass
            ),
            DataProcess(
                task_name="insert_file_table",
                data=paper_input
            )
        ]
        await redis_client.rpush(
            "webview",
            json.dumps({
                "start": True,
                "data": {
                    "url": url,
                    "data_process": [
                        dp.to_dict()
                        for dp in data_process
                    ]
                }
            }, ensure_ascii=False)
        )

        await websocket.send_json({
            "type": "webview",
            "status": "started"
        })
        while True:
            d = await websocket.receive_text()
            print(f"Received from client: {d}")
            if d == "exit":
                break
        
    except WebSocketDisconnect:
        print("Client disconnected from /test")
    
@process_router.websocket("/service/{service_id}")
async def start_process(websocket: WebSocket, service_id: str):

    await websocket.accept()

    try:
        # gọi hàm startProcess từ service
        timestamp = int(time.time())
        service, documents = startProcess(service_id)
        data_ready = {
            "status": False,
            "url": None,
            "data_process": None
        }
        # gửi dữ liệu về client qua websocket
        await websocket.send_json({
            "service": service,
            "documents": documents,
            "code": "0",
            "error": None
        })
        # vòng lặp lắng nghe, phản hồi
        while True:
            data = await websocket.receive_json()
            # xử lý dữ liệu nhận được từ client
            should_continue = await processWebSocket(data, service, documents, timestamp, data_ready, websocket)
            if not should_continue:
                break
    except ValueError as e:
        await websocket.send_json({
            "service": None,
            "documents": None,
            "code": "1",
            "error": str(e)
        })
    except RuntimeError as e:
        await websocket.send_json({
            "service": None,
            "documents": None,
            "code": "2",
            "error": str(e)
        })
    except WebSocketDisconnect:
        print(f"Client disconnected from /start/{service_id}")