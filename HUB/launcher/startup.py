import ctypes
import asyncio
import sys
import threading
import time
import uuid
from pathlib import Path
import base64
import json
import hashlib
import subprocess
from datetime import date

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from redis import Redis

from backend.config import REDIS_HOST, REDIS_PASSWORD, REDIS_PORT
from backend.services.LLMServices import checkLMStudioServerRunning
from backend.services.settingsServices import getMode
from database.index import db


# ============================================================
# UTF-8 CONSOLE
# ============================================================

def _configure_console_encoding():
    """
    PyInstaller trên Windows có thể dùng cp1252 cho stdout/stderr.
    Cấu hình UTF-8 nếu có thể.
    Không để lỗi encoding ảnh hưởng chương trình.
    """
    try:
        if sys.stdout is not None:
            sys.stdout.reconfigure(
                encoding="utf-8",
                errors="replace",
            )
    except Exception:
        pass

    try:
        if sys.stderr is not None:
            sys.stderr.reconfigure(
                encoding="utf-8",
                errors="replace",
            )
    except Exception:
        pass


_configure_console_encoding()


# ============================================================
# BASE DIRECTORY
# ============================================================

def get_base_dir() -> Path:
    """
    Lấy thư mục gốc của HUB.

    Khi chạy Python:
        D:/digital_public_administration_project/HUB

    Khi chạy PyInstaller:
        thư mục chứa HUB.exe
    """
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent

    return Path(__file__).resolve().parents[1]


# ============================================================
# STARTUP GUARD
# ============================================================

class StartupGuard:

    REDIS_LOCK_KEY = "HUB:LOCK"
    REDIS_LOCK_TTL = 30
    REDIS_HEARTBEAT_INTERVAL = 10

    WINDOWS_MUTEX_NAME = "Global\\HUB_BACKEND_SINGLE_INSTANCE"

    def __init__(self):
        self.instance_id = str(uuid.uuid4())

        self.redis_client = Redis(
            host=REDIS_HOST,
            password=REDIS_PASSWORD,
            port=REDIS_PORT,
            db=0,
            decode_responses=True,
        )

        self.mutex_handle = None
        self.redis_lock_acquired = False

        self.stop_event = threading.Event()
        self.heartbeat_thread = None

    # ========================================================
    # ACQUIRE
    # ========================================================

    def acquire(self) -> bool:

        if not self._check_license():
            return False

        while True:

            # --------------------------------------------
            # Windows Mutex
            # --------------------------------------------

            if not self._acquire_windows_mutex():
                print(
                    "[STARTUP] Another HUB instance is already running"
                )
                return False

            try:

                # ----------------------------------------
                # Redis
                # ----------------------------------------

                self.redis_client.ping()

                if not self.redis_client.set(
                    self.REDIS_LOCK_KEY,
                    self.instance_id,
                    nx=True,
                    ex=self.REDIS_LOCK_TTL,
                ):
                    print(
                        "[STARTUP] Another HUB instance owns "
                        "the Redis lock"
                    )

                    self._release_windows_mutex()

                    return False

                self.redis_lock_acquired = True

                # ----------------------------------------
                # Database
                # ----------------------------------------

                if not db.init_pool():

                    print(
                        "[STARTUP] Database is not ready"
                    )

                    self._release_redis_lock()
                    self._release_windows_mutex()

                    print(
                        "[STARTUP] Retrying activation check "
                        "in 5 seconds"
                    )

                    time.sleep(5)

                    continue

                # ----------------------------------------
                # LM Studio
                # ----------------------------------------

                if not self._check_llm_server():

                    self._release_redis_lock()
                    self._release_windows_mutex()

                    print(
                        "[STARTUP] Retrying activation check "
                        "in 5 seconds"
                    )

                    time.sleep(5)

                    continue

                # ----------------------------------------
                # Redis heartbeat
                # ----------------------------------------

                self.heartbeat_thread = threading.Thread(
                    target=self._redis_lock_heartbeat,
                    name="hub-startup-lock-heartbeat",
                    daemon=True,
                )

                self.heartbeat_thread.start()

                print(
                    f"[STARTUP] Activation lock acquired: "
                    f"{self.instance_id}"
                )

                return True

            except Exception as error:

                print(
                    f"[STARTUP] Activation check failed: "
                    f"{error}"
                )

                if self.redis_lock_acquired:
                    self._release_redis_lock()

                self._release_windows_mutex()

                print(
                    "[STARTUP] Retrying activation check "
                    "in 5 seconds"
                )

                time.sleep(5)

    # ========================================================
    # LICENSE
    # ========================================================

    def _check_license(self) -> bool:

        license_path = get_base_dir() / "license.key"

        result = check_license(license_path)

        # --------------------------------------------
        # License hợp lệ
        # --------------------------------------------

        if result.get("valid"):

            print(
                f"[License] Valid until "
                f"{result.get('expire_date', 'unknown')}"
            )

            return True

        # --------------------------------------------
        # License không hợp lệ
        # --------------------------------------------

        reason = result.get(
            "reason",
            "invalid"
        )

        if reason == "missing":

            message = (
                f"Không tìm thấy file license: "
                f"{license_path}."
            )

            title = "HUB - Chưa có license"

        elif reason == "expired":

            message = (
                f"License đã hết hạn "
                f"({result.get('expire_date', 'unknown')})."
            )

            title = "HUB - License hết hạn"

        else:

            message = (
                "License không hợp lệ hoặc "
                "không thuộc máy này."
            )

            title = "HUB - License lỗi"

        message += "\nChương trình sẽ dừng."

        # QUAN TRỌNG:
        #
        # Không print message tiếng Việt.
        #
        # PyInstaller có thể dùng cp1252 và gây:
        #
        # UnicodeEncodeError:
        # 'charmap' codec can't encode character
        #
        # MessageBoxW hỗ trợ Unicode đầy đủ.
        self._show_message(
            message,
            title
        )

        return False

    # ========================================================
    # WINDOWS MESSAGE BOX
    # ========================================================

    @staticmethod
    def _show_message(
        message: str,
        title: str
    ):
        try:

            ctypes.windll.user32.MessageBoxW(
                None,
                str(message),
                str(title),
                0x10,
            )

        except Exception as error:

            # Chỉ fallback sang console.
            # errors="replace" ở trên đảm bảo không crash
            # vì Unicode.
            try:
                print(
                    f"[{title}] {message}"
                )
            except Exception:
                pass

    # ========================================================
    # RELEASE
    # ========================================================

    def release(self):

        self.stop_event.set()

        # --------------------------------------------
        # Heartbeat thread
        # --------------------------------------------

        if (
            self.heartbeat_thread
            and self.heartbeat_thread is not threading.current_thread()
        ):

            self.heartbeat_thread.join(
                timeout=2
            )

            self.heartbeat_thread = None

        # --------------------------------------------
        # Redis lock
        # --------------------------------------------

        if self.redis_lock_acquired:
            self._release_redis_lock()

        # --------------------------------------------
        # Redis connection
        # --------------------------------------------

        try:

            self.redis_client.close()

        except Exception as error:

            print(
                f"[STARTUP] Redis connection close failed: "
                f"{error}"
            )

        # --------------------------------------------
        # Windows mutex
        # --------------------------------------------

        self._release_windows_mutex()

    # ========================================================
    # RELEASE REDIS LOCK
    # ========================================================

    def _release_redis_lock(self):

        try:

            self.redis_client.eval(
                """
                if redis.call("GET", KEYS[1]) == ARGV[1] then
                    return redis.call("DEL", KEYS[1])
                else
                    return 0
                end
                """,
                1,
                self.REDIS_LOCK_KEY,
                self.instance_id,
            )

        except Exception as error:

            print(
                f"[STARTUP] Redis lock release failed: "
                f"{error}"
            )

        finally:

            self.redis_lock_acquired = False

    # ========================================================
    # CHECK LLM SERVER
    # ========================================================

    def _check_llm_server(self) -> bool:

        mode_settings = asyncio.run(
            getMode()
        )

        mode = mode_settings.get(
            "mode",
            "basic"
        )

        # --------------------------------------------
        # Basic mode
        # --------------------------------------------

        if mode not in (
            "server",
            "client",
        ):
            return True

        # --------------------------------------------
        # Server / Client
        # --------------------------------------------

        server_ip = (
            "localhost"
            if mode == "server"
            else mode_settings.get("server_ip")
        )

        if mode == "client" and not server_ip:

            print(
                "[STARTUP] Client mode has no "
                "LM Studio server IP"
            )

            return False

        # --------------------------------------------
        # Check LM Studio
        # --------------------------------------------

        is_running = asyncio.run(
            checkLMStudioServerRunning(
                server_ip
            )
        )

        if not is_running:

            print(
                "[STARTUP] LM Studio server is "
                f"not running: {server_ip}"
            )

        return is_running

    # ========================================================
    # WINDOWS MUTEX
    # ========================================================

    def _acquire_windows_mutex(self) -> bool:

        if self.mutex_handle:
            return True

        kernel32 = ctypes.windll.kernel32

        handle = kernel32.CreateMutexW(
            None,
            False,
            self.WINDOWS_MUTEX_NAME,
        )

        if not handle:
            return False

        # ERROR_ALREADY_EXISTS = 183
        if kernel32.GetLastError() == 183:

            kernel32.CloseHandle(
                handle
            )

            return False

        self.mutex_handle = handle

        return True

    # ========================================================
    # RELEASE WINDOWS MUTEX
    # ========================================================

    def _release_windows_mutex(self):

        if not self.mutex_handle:
            return

        try:

            ctypes.windll.kernel32.ReleaseMutex(
                self.mutex_handle
            )

            ctypes.windll.kernel32.CloseHandle(
                self.mutex_handle
            )

        finally:

            self.mutex_handle = None

    # ========================================================
    # REDIS HEARTBEAT
    # ========================================================

    def _redis_lock_heartbeat(self):

        while not self.stop_event.wait(
            self.REDIS_HEARTBEAT_INTERVAL
        ):

            if not self.redis_lock_acquired:
                return

            try:

                result = self.redis_client.eval(
                    """
                    if redis.call("GET", KEYS[1]) == ARGV[1] then
                        return redis.call("EXPIRE", KEYS[1], ARGV[2])
                    else
                        return 0
                    end
                    """,
                    1,
                    self.REDIS_LOCK_KEY,
                    self.instance_id,
                    self.REDIS_LOCK_TTL,
                )

                if result == 0:

                    print(
                        "[STARTUP] Redis activation "
                        "lock was lost"
                    )

                    self.redis_lock_acquired = False

                    return

            except Exception as error:

                print(
                    f"[STARTUP] Redis lock heartbeat "
                    f"failed: {error}"
                )


# ============================================================
# POWERSHELL
# ============================================================

def _powershell(command: str) -> str:

    try:

        result = subprocess.check_output(
            [
                "powershell",
                "-NoProfile",
                "-NonInteractive",
                "-Command",
                command,
            ],
            stderr=subprocess.DEVNULL,
            text=True,
            encoding="utf-8",
            errors="ignore",
        )

        return result.strip()

    except Exception:

        return ""


# ============================================================
# MACHINE ID
# ============================================================

def get_machine_id() -> str:

    bios_serial = _powershell(
        "(Get-CimInstance Win32_BIOS).SerialNumber"
    )

    machine_guid = _powershell(
        "(Get-ItemProperty "
        "'HKLM:\\SOFTWARE\\Microsoft\\Cryptography').MachineGuid"
    )

    raw = (
        f"{bios_serial}|{machine_guid}"
        .strip()
        .lower()
    )

    return hashlib.sha256(
        raw.encode("utf-8")
    ).hexdigest()


# ============================================================
# AES KEY
# ============================================================

def _get_key(machine_id: str) -> bytes:
    """
    Chuyển machineID thành AES-256 key.
    """

    return hashlib.sha256(
        machine_id.encode("utf-8")
    ).digest()


# ============================================================
# LOAD LICENSE
# ============================================================

def load_license(
    machine_id: str,
    license_file: Path,
):

    try:

        with open(
            license_file,
            "r",
            encoding="utf-8",
        ) as f:

            encrypted_data = (
                f.read()
                .strip()
            )

        if not encrypted_data:
            return None

        # --------------------------------------------
        # Base64 decode
        # --------------------------------------------

        encrypted_bytes = (
            base64.urlsafe_b64decode(
                encrypted_data
            )
        )

        if len(encrypted_bytes) <= 12:
            return None

        # --------------------------------------------
        # AES-GCM
        # --------------------------------------------

        nonce = encrypted_bytes[:12]

        ciphertext = encrypted_bytes[12:]

        key = _get_key(
            machine_id
        )

        aes = AESGCM(
            key
        )

        decrypted_bytes = aes.decrypt(
            nonce,
            ciphertext,
            None,
        )

        # --------------------------------------------
        # JSON
        # --------------------------------------------

        license_data = json.loads(
            decrypted_bytes.decode(
                "utf-8"
            )
        )

        if not isinstance(
            license_data,
            dict,
        ):
            return None

        return license_data

    except Exception as error:

        print(
            f"[License] Load failed: "
            f"{error}"
        )

        return None


# ============================================================
# CHECK LICENSE
# ============================================================

def check_license(
    license_path: Path,
):
    """
    Kiểm tra license hiện tại.

    Return:
        {
            "valid": True/False,
            "reason": ...,
            "expire_date": ...
        }
    """

    # ========================================================
    # FILE KHÔNG TỒN TẠI
    # ========================================================

    if not license_path.exists():

        return {
            "valid": False,
            "reason": "missing",
        }

    # ========================================================
    # MACHINE ID
    # ========================================================

    machine_id = get_machine_id()

    # ========================================================
    # LOAD LICENSE
    # ========================================================

    license_data = load_license(
        machine_id,
        license_path,
    )

    if license_data is None:

        return {
            "valid": False,
            "reason": "invalid",
        }

    # ========================================================
    # CHECK MACHINE ID
    # ========================================================

    license_machine_id = (
        license_data.get(
            "machine_id"
        )
    )

    if license_machine_id != machine_id:

        return {
            "valid": False,
            "reason": "invalid",
        }

    # ========================================================
    # EXPIRE DATE
    # ========================================================

    expire_date_string = (
        license_data.get(
            "expire_date"
        )
    )

    if not expire_date_string:

        return {
            "valid": False,
            "reason": "invalid",
        }

    try:

        expire_date = date.fromisoformat(
            expire_date_string
        )

    except ValueError:

        return {
            "valid": False,
            "reason": "invalid",
        }

    # ========================================================
    # EXPIRED
    # ========================================================

    if date.today() > expire_date:

        return {
            "valid": False,
            "reason": "expired",
            "expire_date": expire_date_string,
        }

    # ========================================================
    # VALID
    # ========================================================

    return {
        "valid": True,
        "reason": None,
        "expire_date": expire_date_string,
        "data": license_data,
    }