import asyncio
import json
import redis.asyncio as redis

from contextlib import asynccontextmanager
from fastapi import APIRouter

from backend.services.scannerServices import (
    checkTWAINinstalled,
    getScannerDevices,
)
from backend.log.main import log_exception

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
            update_scanner_list_devices(10)
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

        await r.delete("scanner_devices:twain")

        await r.aclose()


scanner_router = APIRouter(
    prefix="/scanner",
    lifespan=lifespan,
    tags=["scanner"],
)


# @scanner_router.get("/naps2/installed")
# async def check_naps2_installed():
#     return await checkNAPS2installed()


@scanner_router.get("/twain/installed")
async def check_twain_installed():
    return await checkTWAINinstalled()


@scanner_router.get("/twain/devices")
async def get_scanner_devices():
    return await get_scanner_devices_from_redis()


@scanner_router.get("/twain/options")
async def get_scanner_options():
    devices_by_driver = await get_scanner_devices_from_redis()

    options = []

    for device in devices_by_driver.get("twain", []):
        name = device.get("name", "")
        status = device.get("status", "disconnected")

        if not name:
            continue

        options.append({
            "id": f"twain:{name}",
            "label": name,
            "scanner": name,
            "driver": "twain",
            "status": status,
        })

    selected = next(
        (
            option
            for option in options
            if option["status"] == "connected"
        ),
        None,
    )

    return {
        "options": options,
        "default": selected,
    }


async def update_scanner_list_devices(
    update_interval: int = 10,
):
    key = "scanner_devices:twain"

    while True:
        try:
            new_data_devices = await getScannerDevices()

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
            log_exception(e, "HUB")
            print(
                f"Update TWAIN scanner devices error: {e}"
            )

        await asyncio.sleep(update_interval)


async def get_scanner_devices_from_redis():
    result = {}

    value = await r.get("scanner_devices:twain")
    result["twain"] = json.loads(value) if value else []

    return result