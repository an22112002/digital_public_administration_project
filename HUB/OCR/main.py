from OCR.CCCD import OCR_CCCD, OCR_CCCD2, OCR_CCCD3, OCR_CCCD4
from backend.config import REDIS_HOST, REDIS_PASSWORD, REDIS_PORT
from redis.asyncio import Redis
from uuid import uuid4

redis_client = Redis(
    host=REDIS_HOST, 
    password=REDIS_PASSWORD, 
    port=REDIS_PORT, 
    db=0, 
    decode_responses=True,
    socket_connect_timeout=5,
    socket_timeout=None,
)

# print("REDIS CONNECTION POOL:", redis_client.connection_pool.connection_kwargs)

async def processOCR(code: str, files: list[str]) -> dict | None:
    result = []
    if code == "cccd_husband":
        result = OCR_CCCD(files)
        if result is not None:
            result["type"] = "cccd_husband"
            print(f"result: {result}")
            return result
    if code == "cccd_wife":
        result = OCR_CCCD(files)
        if result is not None:
            result["type"] = "cccd_wife"
            print(f"result: {result}")
            return result
    if code == "cccd_self":
        result = OCR_CCCD(files)
        if result is not None:
            result["type"] = "cccd_self"
            print(f"result: {result}")
            return result
    if code == "cccd_main":
        result = OCR_CCCD(files)
        if result is not None:
            result["type"] = "cccd_main"
            print(f"result: {result}")
            return result
    # mở rộng cho các loại tài liệu khác nếu cần
    return None