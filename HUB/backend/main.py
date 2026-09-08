from redis.asyncio import Redis

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.concurrency import asynccontextmanager
from fastapi.staticfiles import StaticFiles
import asyncio
import ctypes
import uuid

from backend.config import REDIS_HOST, REDIS_PASSWORD, REDIS_PORT, SCANNER_SAVE_PATH

from backend.routers.scannerRouter import scanner_router
from backend.routers.settingsRouter import settings_router
from backend.routers.processRouter import process_router
from backend.routers.serviceRouter import service_router

from backend.worker.Manager import WorkerManager
from backend.log.main import install_exception_hooks, log_exception
from database.index import db

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

    REDIS_LOCK_KEY = "HUB:LOCK"
    REDIS_LOCK_TTL = 30
    REDIS_HEARTBEAT_INTERVAL = 10

    WINDOWS_MUTEX_NAME = "Global\\HUB_BACKEND_SINGLE_INSTANCE"

    # ==========================================================
    # INIT
    # ==========================================================

    def __init__(self, host: str = "0.0.0.0", port: int = 8000):

        self.host = host
        self.port = port

        # ------------------------------------------------------
        # Unique ID cho instance HUB này
        # ------------------------------------------------------

        self.hub_id = str(uuid.uuid4())

        # ------------------------------------------------------
        # Windows Mutex
        # ------------------------------------------------------

        self.mutex_handle = None

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
        # Lock state
        # ------------------------------------------------------

        self.redis_lock_acquired = False
        self.heartbeat_task = None

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

        print("[Start] Starting HUB backend...")
        install_exception_hooks("HUB")

        windows_mutex_acquired = False
        redis_lock_acquired = False
        worker_started = False

        try:

            # ==================================================
            # 1. WINDOWS MUTEX
            # ==================================================

            if not self.acquire_windows_mutex():

                print(
                    "[Error] Another HUB instance "
                    "is already running"
                )

                app.state.should_exit = True

                # Không start bất kỳ thứ gì
                return

            windows_mutex_acquired = True

            print("[Start] Windows mutex acquired")

            # ==================================================
            # 2. REDIS
            # ==================================================

            response = await self.redis_client.ping()

            if not response:

                raise RuntimeError(
                    "Redis connection failed"
                )

            print("[Start] Redis connection successful")

            # ==================================================
            # 3. REDIS LOCK
            # ==================================================

            if not await self.acquire_redis_lock():

                print(
                    "[Error] Another HUB instance "
                    "already owns the Redis lock"
                )

                app.state.should_exit = True

                return

            redis_lock_acquired = True

            print(
                f"[Start] Redis lock acquired: {self.hub_id}"
            )

            # ==================================================
            # 4. HEARTBEAT
            # ==================================================

            self.heartbeat_task = asyncio.create_task(
                self.redis_lock_heartbeat()
            )

            # ==================================================
            # 5. DATABASE
            # ==================================================

            response = db.init_pool()

            if not response:

                raise RuntimeError(
                    "Database connection failed"
                )

            print(
                "[Start] Database connection successful"
            )

            # ==================================================
            # 6. CLEAR REDIS
            # ==================================================

            await self.clear_hub_redis_data()

            print(
                "[Start] Old HUB Redis data cleared"
            )

            # ==================================================
            # 7. WORKER
            # ==================================================

            await self.worker_manager.start()

            worker_started = True

            print(
                "[Start] WorkerManager started"
            )

            print(
                "[Start] HUB backend started"
            )

            # ==================================================
            # RUNNING
            # ==================================================

            yield

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
            # STOP HEARTBEAT
            # ==================================================

            if self.heartbeat_task:

                self.heartbeat_task.cancel()

                try:

                    await self.heartbeat_task

                except asyncio.CancelledError:

                    pass

                self.heartbeat_task = None

            # ==================================================
            # RELEASE REDIS LOCK
            # ==================================================

            if redis_lock_acquired:

                try:

                    await self.release_redis_lock()

                    print(
                        "[End] Redis lock released"
                    )

                except Exception as e:

                    log_exception(e, "HUB")

                    print(
                        f"[Error] Redis lock release failed: {e}"
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

            # ==================================================
            # RELEASE WINDOWS MUTEX
            # ==================================================

            if windows_mutex_acquired:

                self.release_windows_mutex()

                print(
                    "[End] Windows mutex released"
                )

            print(
                "[End] HUB backend shutdown"
            )

    # ==========================================================
    # WINDOWS MUTEX
    # ==========================================================

    def acquire_windows_mutex(self) -> bool:

        if self.mutex_handle:

            return True

        ERROR_ALREADY_EXISTS = 183

        kernel32 = ctypes.windll.kernel32

        handle = kernel32.CreateMutexW(
            None,
            False,
            self.WINDOWS_MUTEX_NAME,
        )

        if not handle:

            print(
                "[Error] Cannot create Windows mutex"
            )

            return False

        last_error = kernel32.GetLastError()

        if last_error == ERROR_ALREADY_EXISTS:

            kernel32.CloseHandle(handle)

            return False

        self.mutex_handle = handle

        return True

    # ==========================================================

    def release_windows_mutex(self):

        if not self.mutex_handle:

            return

        try:

            ctypes.windll.kernel32.ReleaseMutex(
                self.mutex_handle
            )

        except Exception as e:

            log_exception(e, "HUB")

        try:

            ctypes.windll.kernel32.CloseHandle(
                self.mutex_handle
            )

        except Exception as e:

            log_exception(e, "HUB")


        self.mutex_handle = None

    # ==========================================================
    # REDIS LOCK
    # ==========================================================

    async def acquire_redis_lock(self) -> bool:

        result = await self.redis_client.set(
            self.REDIS_LOCK_KEY,
            self.hub_id,
            nx=True,
            ex=self.REDIS_LOCK_TTL,
        )

        if result:

            self.redis_lock_acquired = True

            return True

        return False

    # ==========================================================

    async def release_redis_lock(self):

        if not self.redis_lock_acquired:

            return

        # Chỉ delete nếu lock vẫn thuộc về HUB này.
        #
        # Không dùng:
        #
        # await redis.delete(KEY)
        #
        # vì lock có thể đã hết hạn và được HUB khác lấy.

        script = """
        if redis.call("GET", KEYS[1]) == ARGV[1] then
            return redis.call("DEL", KEYS[1])
        else
            return 0
        end
        """

        try:

            await self.redis_client.eval(
                script,
                1,
                self.REDIS_LOCK_KEY,
                self.hub_id,
            )

        finally:

            self.redis_lock_acquired = False

    # ==========================================================
    # REDIS HEARTBEAT
    # ==========================================================

    async def redis_lock_heartbeat(self):

        while True:

            try:

                await asyncio.sleep(
                    self.REDIS_HEARTBEAT_INTERVAL
                )

                if not self.redis_lock_acquired:

                    return

                # Chỉ gia hạn nếu lock vẫn thuộc HUB này.

                script = """
                if redis.call("GET", KEYS[1]) == ARGV[1] then
                    return redis.call("EXPIRE", KEYS[1], ARGV[2])
                else
                    return 0
                end
                """

                result = await self.redis_client.eval(
                    script,
                    1,
                    self.REDIS_LOCK_KEY,
                    self.hub_id,
                    self.REDIS_LOCK_TTL,
                )

                if result == 0:

                    print(
                        "[Error] Redis HUB lock was lost"
                    )

                    self.redis_lock_acquired = False

                    return

            except asyncio.CancelledError:

                return

            except Exception as e:

                log_exception(e, "HUB")

                print(
                    f"[Error] Redis heartbeat failed: {e}"
                )

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

                if key == self.REDIS_LOCK_KEY:

                    continue

                keys.append(key)

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
    uvicorn.run(backend.get_app(), host=backend.host, port=backend.port)
    # uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload