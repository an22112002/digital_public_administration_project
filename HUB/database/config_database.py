import os
import sys
from pathlib import Path


# =========================================================
# Base directory
# =========================================================

if getattr(sys, "frozen", False):
    BASE_DIR = Path(sys.executable).resolve().parent
else:
    BASE_DIR = Path(__file__).resolve().parent.parent


# =========================================================
# Default config
# =========================================================

database_config = {
    "pool_size": 10,
    "host": "127.0.0.1",
    "port": 3308,
    "user": "hub_user",
    "password": "2e95b4d498fab9ed41cfc3a3d6ec58e9069b31b71057391a1a6ca2cef739faa3",
    "database": "HUB_db",
}


# =========================================================
# External config
# =========================================================

CONFIG_PATH = BASE_DIR / "config.txt"


if CONFIG_PATH.exists():

    with open(CONFIG_PATH, "r", encoding="utf-8") as f:

        for line in f:

            line = line.strip()

            if not line or line.startswith("#"):
                continue

            if "=" not in line:
                continue

            key, value = line.split("=", 1)

            key = key.strip()
            value = value.strip()

            if key not in database_config:
                continue

            if key in ("pool_size", "port"):
                database_config[key] = int(value)
            else:
                database_config[key] = value


# =========================================================
# Export
# =========================================================

host = database_config["host"]
port = database_config["port"]
user = database_config["user"]
password = database_config["password"]
database = database_config["database"]
pool_size = database_config["pool_size"]