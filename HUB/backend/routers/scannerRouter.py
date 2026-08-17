import asyncio
import json
import redis.asyncio as redis

from contextlib import asynccontextmanager
from fastapi import APIRouter

from backend.services.scannerServices import (
    checkNAPS2installed,
    getScannerDevices,
)

from backend.config import (
    REDIS_HOST,
    REDIS_PASSWORD,
    REDIS_PORT,
)


r = redis.Redis(
    host=REDIS_HOST,
    password=REDIS_PASSWORD,
    port=REDIS_PORT,
    db=0,
    decode_responses=True,
)


@asynccontextmanager
async def lifespan(router: APIRouter):
    tasks = [
        asyncio.create_task(
            update_scanner_list_devices("wia", 10)
        ),
        asyncio.create_task(
            update_scanner_list_devices("twain", 10)
        ),
        asyncio.create_task(
            update_scanner_list_devices("escl", 10)
        ),
    ]

    try:
        yield

    finally:
        for task in tasks:
            task.cancel()

        await asyncio.gather(
            *tasks,
            return_exceptions=True,
        )

        for driver in ("wia", "twain", "escl"):
            await r.delete(
                f"scanner_devices:{driver}"
            )

        await r.aclose()


scanner_router = APIRouter(
    prefix="/scanner",
    lifespan=lifespan,
    tags=["scanner"],
)


@scanner_router.get("/naps2/installed")
async def check_naps2_installed():
    return await checkNAPS2installed()


@scanner_router.get("/naps2/devices")
async def get_scanner_devices():
    return await get_scanner_devices_from_redis()


async def update_scanner_list_devices(
    type_driver: str,
    update_interval: int = 10,
):
    key = f"scanner_devices:{type_driver}"

    while True:
        try:
            new_data_devices = await getScannerDevices(type_driver)

            value = await r.get(key)

            if value:
                data = json.loads(value)
            else:
                data = []

            new_names = set(new_data_devices)

            # Update thiết bị cũ
            for device in data:
                device["status"] = (
                    "connected"
                    if device["name"] in new_names
                    else "disconnected"
                )

            # Thêm thiết bị mới
            old_names = {
                device["name"]
                for device in data
            }

            for name in new_data_devices:
                if name not in old_names:
                    data.append({
                        "name": name,
                        "status": "connected",
                    })

            await r.set(
                key,
                json.dumps(data, ensure_ascii=False),
            )

        except asyncio.CancelledError:
            raise

        except Exception as e:
            print(
                f"Update scanner devices "
                f"{type_driver} error: {e}"
            )

        await asyncio.sleep(update_interval)


async def get_scanner_devices_from_redis():
    result = {}

    for driver in ("wia", "twain", "escl"):
        value = await r.get(
            f"scanner_devices:{driver}"
        )

        if value:
            result[driver] = json.loads(value)
        else:
            result[driver] = []

    return result