from redis.asyncio import Redis

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.concurrency import asynccontextmanager
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from backend.config import REDIS_HOST, REDIS_PASSWORD, REDIS_PORT

from backend.routers.scannerRouter import scanner_router
from backend.routers.settingsRouter import settings_router
from backend.routers.processRouter import process_router
from backend.routers.serviceRouter import service_router

from backend.worker.Manager import WorkerManager
from database.index import db

redis_client = Redis(host=REDIS_HOST, password=REDIS_PASSWORD, port=REDIS_PORT, db=0, decode_responses=True)
worker_manager = WorkerManager()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Khởi động server
    print("[Start] Starting...")
    try:
        response = db.init_pool()
        if response:
            print("[Start] Database connection successful")
        else:
            print("[Error] Database connection failed")
            raise Exception("Database connection failed")
        response = redis_client.ping()
        if response:
            print("[Start] Redis connection successful")
        else:
            print("[Error] Redis connection failed")
            raise Exception("Redis connection failed")
        await worker_manager.start()
    except Exception as e:
        print(f"[Error] Khởi động server thất bại: {e}")
        # Dừng khởi động server nếu có lỗi
        raise
    yield
    await worker_manager.stop()
    # Kết thúc server
    print("[End] Shutdown")

app = FastAPI(lifespan=lifespan)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(settings_router)
app.include_router(scanner_router)
app.include_router(process_router)
app.include_router(service_router)

@app.get("/ping")
def pong():
    return {"message": "pong"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
    # uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload