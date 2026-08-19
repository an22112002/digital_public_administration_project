from urllib import request
import time

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from backend.services.processServices import getActiveServices, processWebSocket, startProcess

from backend.models.processModels import StartProcessResponse

process_router = APIRouter(prefix="/process", tags=["process"])
    
@process_router.websocket("/ws/{service_id}")
async def start_process(websocket: WebSocket, service_id: str):
    await websocket.accept()
    try:
        # gọi hàm startProcess từ service
        timestamp = int(time.time())
        service, documents = startProcess(service_id)
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
            should_continue = await processWebSocket(data, service, documents, timestamp, websocket)
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