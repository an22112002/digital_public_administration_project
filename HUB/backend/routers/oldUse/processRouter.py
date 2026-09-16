import time, asyncio, shutil, os
from pathlib import Path

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from backend.services.processServices import processWebSocket, startProcess
from backend.log.main import log_exception
from contextlib import asynccontextmanager

# ----------------------------------
from backend.config import REDIS_HOST, REDIS_PASSWORD, REDIS_PORT, SCANNER_SAVE_PATH
from redis.asyncio import Redis

redis_client = Redis(host=REDIS_HOST, password=REDIS_PASSWORD, port=REDIS_PORT, db=0, decode_responses=True)
#----------------------------------
SCANNER_SAVE = Path(SCANNER_SAVE_PATH)
PATCH_PREFIX = "patch_"

PATCH_EXPIRE_SECONDS = 5 * 60   # 5 phút
CLEANUP_INTERVAL_SECONDS = 3 * 60   # 3 phút

working_timestamps: set[int] = set()

@asynccontextmanager
async def lifespan(router: APIRouter):

    cleanup_task = asyncio.create_task(
        cleanup_old_patch_folders()
    )

    try:
        yield

    finally:
        cleanup_task.cancel()

        await asyncio.gather(
            cleanup_task,
            return_exceptions=True,
        )

process_router = APIRouter(prefix="/process", lifespan=lifespan, tags=["process"])


 
@process_router.websocket("/service/{service_id}")
async def start_process(websocket: WebSocket, service_id: str):

    await websocket.accept()

    try:
        # gọi hàm startProcess từ service
        timestamp = int(time.time())
        working_timestamps.add(timestamp)
        service, documents = startProcess(service_id)
        for doc in documents:
            doc["srID"] = str(doc["srID"])
            doc["required"] = bool(doc["required"])
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
    finally:
        working_timestamps.discard(timestamp)

# xóa các folder patch cũ sau một khoảng thời gian
async def cleanup_old_patch_folders():
    """
    Tự động xóa các patch_<timestamp> đã cũ hơn 5 phút.

    Không xóa các patch đang nằm trong working_timestamps.
    """

    while True:
        try:
            now = int(time.time())
            expire_timestamp = now - PATCH_EXPIRE_SECONDS

            if SCANNER_SAVE.exists():
                for folder in SCANNER_SAVE.iterdir():

                    # Không phải folder
                    if not folder.is_dir():
                        continue

                    # Không đúng format patch_<timestamp>
                    if not folder.name.startswith(PATCH_PREFIX):
                        continue

                    timestamp_text = folder.name[len(PATCH_PREFIX):]

                    # timestamp không hợp lệ
                    if not timestamp_text.isdigit():
                        continue

                    timestamp = int(timestamp_text)

                    # ------------------------------------------------
                    # Đang được sử dụng -> KHÔNG XÓA
                    # ------------------------------------------------
                    if timestamp in working_timestamps:
                        continue

                    # ------------------------------------------------
                    # Chưa quá 5 phút -> KHÔNG XÓA
                    # ------------------------------------------------
                    if timestamp > expire_timestamp:
                        continue

                    # ------------------------------------------------
                    # Đã quá 5 phút -> XÓA
                    # ------------------------------------------------
                    try:
                        shutil.rmtree(folder)

                    except Exception as e:
                        log_exception(e, "HUB")
                        print(
                            f"[CLEANUP] Failed to delete "
                            f"{folder}: {e}"
                        )

        except Exception as e:
            log_exception(e, "HUB")
            print(f"[CLEANUP] Error: {e}")

        # Chờ trước lần cleanup tiếp theo
        await asyncio.sleep(CLEANUP_INTERVAL_SECONDS)