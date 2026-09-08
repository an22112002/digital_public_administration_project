import asyncio
from backend.worker.webViewWorker import WebViewWorker
from backend.worker.OCRWorker import OCRWorker
from redis.asyncio import Redis
import multiprocessing

from backend.config import REDIS_HOST, REDIS_PASSWORD, REDIS_PORT
from backend.log.main import install_exception_hooks

redis_client_manager = Redis(host=REDIS_HOST, password=REDIS_PASSWORD, port=REDIS_PORT, db=0, decode_responses=True)

# def ocr_worker_main():

#     asyncio.run(
#         ocr_process_main()
#     )


# async def ocr_process_main():

#     install_exception_hooks("worker")

#     redis_client = Redis(
#         host=REDIS_HOST,
#         port=REDIS_PORT,
#         password=REDIS_PASSWORD,
#         db=0,
#         decode_responses=True
#     )

#     try:

#         worker = OCRWorker(
#             redis_client
#         )

#         await worker.run()

#     finally:

#         await redis_client.aclose()


def webview_worker_main():

    asyncio.run(
        webview_process_main()
    )


async def webview_process_main():

    install_exception_hooks("worker")

    redis_client = Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        password=REDIS_PASSWORD,
        db=0,
        decode_responses=True
    )

    try:

        worker = WebViewWorker(
            redis_client
        )

        await worker.run()

    finally:

        await redis_client.aclose()

class WorkerManager:

    def __init__(self):

        self.worker_names = [
            "webview",
            # "ocr"
        ]

        self.processes = {}

    async def start(self):

        print("[WORKER MANAGER] Starting...")

        # ============================================
        # INIT STATE
        # ============================================

        for name in self.worker_names:

            await redis_client_manager.hset(
                f"worker:{name}",
                mapping={
                    "allow": "1",
                    "running": "0"
                }
            )

        # ============================================
        # WEBVIEW PROCESS
        # ============================================

        webview_process = multiprocessing.Process(
            target=webview_worker_main,
            daemon=False
        )

        webview_process.start()

        self.processes["webview"] = webview_process

        print(
            f"[WORKER MANAGER] "
            f"WebView PID={webview_process.pid}"
        )

        # ============================================
        # OCR PROCESS
        # ============================================

        # ocr_process = multiprocessing.Process(
        #     target=ocr_worker_main,
        #     daemon=False
        # )

        # ocr_process.start()

        # self.processes["ocr"] = ocr_process

        # print(
        #     f"[WORKER MANAGER] "
        #     f"OCR PID={ocr_process.pid}"
        # )

        print(
            "[WORKER MANAGER] All workers started"
        )

    async def stop(self):

        print(
            "[WORKER MANAGER] "
            "Stopping workers..."
        )

        # ==================================================
        # 1. REQUEST STOP
        # ==================================================

        for name in self.worker_names:

            await redis_client_manager.hset(
                f"worker:{name}",
                "allow",
                "0"
            )

        print(
            "[WORKER MANAGER] "
            "Stop requested"
        )

        # ==================================================
        # 2. CHỜ WORKER TỰ DỪNG
        # ==================================================

        timeout = 10
        elapsed = 0

        while elapsed < timeout:

            all_stopped = True

            for name in self.worker_names:

                running = await redis_client_manager.hget(
                    f"worker:{name}",
                    "running"
                )

                print(
                    f"[WORKER MANAGER] "
                    f"{name}: running={running}"
                )

                if running == "1":

                    all_stopped = False
                    break

            if all_stopped:
                print(
                    "[WORKER MANAGER] "
                    "All workers reported stopped"
                )
                break

            await asyncio.sleep(0.5)

            elapsed += 0.5

        # ==================================================
        # 3. KIỂM TRA PROCESS THỰC TẾ
        # ==================================================

        for name, process in self.processes.items():

            if process is None:
                continue

            if process.is_alive():

                print(
                    f"[WORKER MANAGER] "
                    f"{name} PID={process.pid} "
                    f"still alive -> terminate"
                )

                process.terminate()

                await asyncio.to_thread(
                    process.join,
                    5
                )

            else:

                print(
                    f"[WORKER MANAGER] "
                    f"{name} PID={process.pid} "
                    f"already exited"
                )

        # ==================================================
        # 4. CLEAR
        # ==================================================

        self.processes.clear()

        print(
            "[WORKER MANAGER] "
            "All workers stopped"
        )