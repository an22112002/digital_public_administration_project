from OCR.CCCD import CCCD_LLM
from backend.config import REDIS_HOST, REDIS_PASSWORD, REDIS_PORT
from redis.asyncio import Redis

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
async def processOCR2(code: str, files: list[str], server_ip: str) -> dict | None:
    try:
        result = []
        if code == "cccd_husband":
            result = await CCCD_LLM(files, server_ip)
            if result is not None:
                result["type"] = "cccd_husband"
                print(f"result: {result}")
                return result
        if code == "cccd_wife":
            result = await CCCD_LLM(files, server_ip)
            if result is not None:
                result["type"] = "cccd_wife"
                print(f"result: {result}")
                return result
        if code == "cccd_self":
            result = await CCCD_LLM(files, server_ip)
            if result is not None:
                result["type"] = "cccd_self"
                print(f"result: {result}")
                return result
        if code == "cccd_main":
            result = await CCCD_LLM(files, server_ip)
            if result is not None:
                result["type"] = "cccd_main"
                print(f"result: {result}")
                return result
        # mở rộng cho các loại tài liệu khác nếu cần
        return None
    except Exception as e:
        print(f"Error in processOCR2: {e}")
        return None

# async def processOCR(code: str, files: list[str]) -> dict | None:
#     result = []
#     if code == "cccd_husband":
#         result = await OCR_CCCD2(files, redis_client, str(uuid4()))
#         if result is not None:
#             result["type"] = "cccd_husband"
#             print(f"result: {result}")
#             return result
#     if code == "cccd_wife":
#         result = await OCR_CCCD2(files, redis_client, str(uuid4()))
#         if result is not None:
#             result["type"] = "cccd_wife"
#             print(f"result: {result}")
#             return result
#     if code == "cccd_self":
#         result = await OCR_CCCD2(files, redis_client, str(uuid4()))
#         if result is not None:
#             result["type"] = "cccd_self"
#             print(f"result: {result}")
#             return result
#     if code == "cccd_main":
#         result = await OCR_CCCD2(files, redis_client, str(uuid4()))
#         if result is not None:
#             result["type"] = "cccd_main"
#             print(f"result: {result}")
#             return result
#     # mở rộng cho các loại tài liệu khác nếu cần
#     return None