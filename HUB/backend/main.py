from redis.asyncio import Redis

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.concurrency import asynccontextmanager
from fastapi.staticfiles import StaticFiles

from backend.config import REDIS_HOST, REDIS_PASSWORD, REDIS_PORT, SCANNER_SAVE_PATH

from backend.routers.scannerRouter import scanner_router
from backend.routers.settingsRouter import settings_router
from backend.routers.processRouter import process_router
from backend.routers.serviceRouter import service_router

from backend.services.settingsServices import getMode
from backend.services.LLMServices import loadLocalLMStudioModel, unloadLocalLMStudioModel

from backend.worker.Manager import WorkerManager
from backend.log.main import install_exception_hooks, log_exception

import webbrowser
import asyncio
import httpx
from backend.config import open_settings

redis_client = Redis(host=REDIS_HOST, password=REDIS_PASSWORD, port=REDIS_PORT, db=0, decode_responses=True)
worker_manager = WorkerManager()

# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     # Khởi động server
#     print("[Start] Starting...")
#     try:
#         response = db.init_pool()
#         if response:
#             print("[Start] Database connection successful")
#         else:
#             print("[Error] Database connection failed")
#             raise Exception("Database connection failed")
#         response = redis_client.ping()
#         if response:
#             print("[Start] Redis connection successful")
#         else:
#             print("[Error] Redis connection failed")
#             raise Exception("Redis connection failed")
#         await worker_manager.start()
#     except Exception as e:
#         print(f"[Error] Khởi động server thất bại: {e}")
#         # Dừng khởi động server nếu có lỗi
#         raise
#     yield
#     await worker_manager.stop()
#     # Kết thúc server
#     print("[End] Shutdown")

# app = FastAPI(lifespan=lifespan)

# app.mount("/scanned-files", 
#           StaticFiles(directory=SCANNER_SAVE_PATH),
#           name="scanned-files")

# # CORS Middleware
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# app.include_router(settings_router)
# app.include_router(scanner_router)
# app.include_router(process_router)
# app.include_router(service_router)

# @app.get("/ping")
# def pong():
    # return {"message": "pong"}

class Backend:

    # ==========================================================
    # CONFIG
    # ==========================================================

    # ==========================================================
    # INIT
    # ==========================================================

    def __init__(self, host: str = "0.0.0.0", port: int = 8000):

        self.host = host
        self.port = port

        self.mode = "basic"
        self.server_ip = None
        self.on_started = None

        # ------------------------------------------------------
        # Redis
        # ------------------------------------------------------

        self.redis_client = Redis(
            host=REDIS_HOST,
            password=REDIS_PASSWORD,
            port=REDIS_PORT,
            db=0,
            decode_responses=True,
        )

        # ------------------------------------------------------
        # Worker
        # ------------------------------------------------------

        self.worker_manager = WorkerManager()

        # ------------------------------------------------------
        # FastAPI
        # ------------------------------------------------------

        self.app = FastAPI(
            lifespan=self.lifespan
        )

        self._setup_static()
        self._setup_cors()
        self._setup_routers()

        self.add_ping_route()

    # ==========================================================
    # LIFESPAN
    # ==========================================================
    @asynccontextmanager
    async def lifespan(self, app: FastAPI):
        mode = await getMode()
        self.mode = mode.get("mode", "basic")
        self.server_ip = mode.get("server_ip", None)

        print("[Start] Starting HUB backend...")
        install_exception_hooks("HUB")

        worker_started = False

        try:

            # ==================================================
            # CLEAR REDIS
            # ==================================================

            await self.clear_hub_redis_data()

            print(
                "[Start] Old HUB Redis data cleared"
            )

            # ==================================================
            # WORKER
            # ==================================================

            await self.worker_manager.start()

            worker_started = True

            print(
                "[Start] WorkerManager started"
            )

            print(
                "[Start] HUB backend started"
            )

            # =================================================
            # MODE
            # =================================================
            if self.mode == "basic":
                print("[Start] Running in BASIC mode")
            elif self.mode == "server":
                await loadLocalLMStudioModel()
                print("[Start] Running in SERVER mode")
            elif self.mode == "client":
                print("[Start] Running in CLIENT mode")

            if self.on_started:
                self.on_started()

            asyncio.create_task(self.startup())

            # ==================================================
            # RUNNING
            # ==================================================

            yield

        except SystemExit:

            # Không log gì cả, chỉ exit ngay lập tức.

            raise

        except Exception as e:

            log_exception(e, "HUB")

            print(
                f"[Error] HUB startup failed: {e}"
            )

            raise

        finally:

            print(
                "[End] Shutting down HUB backend..."
            )
            # =================================================
            ## UNLOAD LLM MODEL
            # =================================================
            if self.mode == "server":
                try:
                    await unloadLocalLMStudioModel()
                except Exception as e:
                    log_exception(e, "HUB")
                    print(f"[Error] LLM model unload failed: {e}")

            # ==================================================
            # STOP WORKER
            # ==================================================

            if worker_started:

                try:

                    print(
                        "[End] Stopping WorkerManager..."
                    )

                    await self.worker_manager.stop()

                    print(
                        "[End] WorkerManager stopped"
                    )

                except Exception as e:

                    log_exception(e, "HUB")

                    print(
                        f"[Error] Worker shutdown failed: {e}"
                    )

            else:

                print(
                    "[End] WorkerManager was not started"
                )

            # ==================================================
            # CLOSE REDIS
            # ==================================================

            try:

                await self.redis_client.close()

                print(
                    "[End] Redis connection closed"
                )

            except Exception as e:

                log_exception(e, "HUB")

                print(
                    f"[Error] Redis shutdown failed: {e}"
                )

            print(
                "[End] HUB backend shutdown"
            )

    async def startup(self):
        settings_data = await open_settings()

        if not settings_data.get("settings", {}).get("autoStart", False):
            return

        ui = settings_data.get("settings", {}).get("ui", "desktop")

        while True:
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get( "http://127.0.0.1:8000/ping", timeout=1)

                if response.status_code == 200:
                    break

            except Exception:
                pass

            await asyncio.sleep(1)

        webbrowser.open(f"http://localhost:5174/{ui}")

    # ==========================================================
    # CLEAR HUB REDIS DATA
    # ==========================================================

    async def clear_hub_redis_data(self):

        """
        Không dùng FLUSHDB.

        Chỉ xóa các key thuộc HUB.
        """

        patterns = [
            "HUB:*",
            "ocr:*",
            "worker:*"
        ]

        for pattern in patterns:

            keys = []

            async for key in self.redis_client.scan_iter(
                match=pattern
            ):

                # Không xóa lock hiện tại.

                key_name = (
                    key.decode()
                    if isinstance(key, bytes)
                    else key
                )

                if key_name == "HUB:LOCK":

                    continue

                keys.append(key_name)

            if keys:

                await self.redis_client.delete(*keys)

    # ==========================================================
    # STATIC
    # ==========================================================

    def _setup_static(self):

        self.app.mount(
            "/scanned-files",
            StaticFiles(
                directory=SCANNER_SAVE_PATH
            ),
            name="scanned-files",
        )

    # ==========================================================
    # CORS
    # ==========================================================

    def _setup_cors(self):

        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # ==========================================================
    # ROUTERS
    # ==========================================================

    def _setup_routers(self):

        self.app.include_router(
            settings_router
        )

        self.app.include_router(
            scanner_router
        )

        self.app.include_router(
            process_router
        )

        self.app.include_router(
            service_router
        )

    # ==========================================================
    # PING
    # ==========================================================

    def add_ping_route(self):

        @self.app.get("/ping")
        def pong():

            return {
                "message": "pong"
            }

    # ==========================================================
    # APP
    # ==========================================================

    def get_app(self) -> FastAPI:

        return self.app

if __name__ == "__main__":
    import uvicorn
    backend = Backend()
    uvicorn.run(
        backend.get_app(),
        host=backend.host,
        port=backend.port,
        timeout_graceful_shutdown=5,
    )
    # uvicorn backend.main:app --host 0.0.0.0 --port 8000 --relo