import base64
import json
import os
import subprocess
import sys
import threading
import webbrowser
import asyncio

from datetime import date
from pathlib import Path

import pystray
from PIL import Image
from pystray import MenuItem
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from backend.config import open_settings
from launcher.startup import get_machine_id, _get_key


# ============================================================
# PATH
# ============================================================

def get_base_dir() -> Path:
    """
    Lấy thư mục chứa HUB.exe khi build PyInstaller.
    Khi chạy bằng Python thì lấy thư mục chứa file Python hiện tại.
    """

    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent

    return Path(__file__).resolve().parents[1]


BASE_DIR = get_base_dir()


# ============================================================
# EDGE
# ============================================================

EDGE_PATH_1 = Path(
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
)

EDGE_PATH_2 = Path(
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"
)

if EDGE_PATH_1.exists():
    EDGE_PATH = EDGE_PATH_1
elif EDGE_PATH_2.exists():
    EDGE_PATH = EDGE_PATH_2
else:
    EDGE_PATH = None


# ============================================================
# TRAY APP
# ============================================================

class TrayApp:

    STATUS_STARTING = "Đang khởi động"
    STATUS_RUNNING = "Đang chạy"
    STATUS_CLOSING = "Đang đóng"

    def __init__(self, server):

        self.server = server

        self.icon = None

        self.ip = "localhost"

        self.status = self.STATUS_STARTING

        # License
        self.license_valid = False
        self.license_reason = None
        self.license_data = None
        self.license_status = None

    # ========================================================
    # STATUS
    # ========================================================

    def set_status(self, status):

        self.status = status

        if self.icon:
            self.icon.update_menu()

    def status_label(self, item):

        return f"Trạng thái: {self.status}"

    def set_running_status(self):

        self.set_status(
            self.STATUS_RUNNING
        )

    # ========================================================
    # LICENSE
    # ========================================================

    def get_license_path(self) -> Path:

        return BASE_DIR / "license.key"

    def load_license(
        self,
        machine_id: str,
        license_file: Path
    ):
        """
        Đọc và giải mã license.key bằng machine_id.
        """

        try:

            with open(
                license_file,
                "r",
                encoding="utf-8"
            ) as f:

                encrypted_data = f.read().strip()

            if not encrypted_data:
                print("License file is empty")
                return None

            # Base64 decode
            try:

                encrypted_bytes = base64.urlsafe_b64decode(
                    encrypted_data
                )

            except Exception as e:

                print(
                    f"Invalid Base64 license: {e}"
                )

                return None

            # AES-GCM:
            # 12 bytes nonce
            # phần còn lại ciphertext + authentication tag

            if len(encrypted_bytes) <= 12:

                print("Invalid encrypted license length")

                return None

            nonce = encrypted_bytes[:12]

            ciphertext = encrypted_bytes[12:]

            # Tạo key từ machine ID
            key = _get_key(machine_id)

            aes = AESGCM(key)

            # Giải mã
            decrypted_bytes = aes.decrypt(
                nonce,
                ciphertext,
                None
            )

            # JSON decode
            license_data = json.loads(
                decrypted_bytes.decode("utf-8")
            )

            if not isinstance(
                license_data,
                dict
            ):
                print("License JSON is not an object")
                return None

            return license_data

        except Exception as e:

            print(
                f"Failed to load license: {e}"
            )

            return None

    def check_license(self):

        license_path = self.get_license_path()

        print("--------------------------------")
        print("Checking license...")
        print(f"BASE_DIR    : {BASE_DIR}")
        print(f"License path: {license_path}")
        print(f"Exists      : {license_path.exists()}")

        # ----------------------------------------------------
        # Không có file
        # ----------------------------------------------------

        if not license_path.exists():

            return {
                "valid": False,
                "reason": "missing"
            }

        # ----------------------------------------------------
        # Lấy machine ID
        # ----------------------------------------------------

        machine_id = get_machine_id()

        print(
            f"Machine ID: {machine_id}"
        )

        # ----------------------------------------------------
        # Giải mã license
        # ----------------------------------------------------

        license_data = self.load_license(
            machine_id,
            license_path
        )

        if license_data is None:

            return {
                "valid": False,
                "reason": "invalid"
            }

        print(
            f"License data: {license_data}"
        )

        # ----------------------------------------------------
        # Kiểm tra machine_id trong JSON
        # ----------------------------------------------------

        license_machine_id = license_data.get(
            "machine_id"
        )

        if not license_machine_id:

            print(
                "License does not contain machine_id"
            )

            return {
                "valid": False,
                "reason": "invalid"
            }

        if license_machine_id != machine_id:

            print(
                "Machine ID mismatch"
            )

            return {
                "valid": False,
                "reason": "invalid"
            }

        # ----------------------------------------------------
        # Kiểm tra expire_date
        # ----------------------------------------------------

        expire_date_string = license_data.get(
            "expire_date"
        )

        if not expire_date_string:

            print(
                "License does not contain expire_date"
            )

            return {
                "valid": False,
                "reason": "invalid"
            }

        try:

            expire_date = date.fromisoformat(
                expire_date_string
            )

        except ValueError:

            print(
                f"Invalid expire_date: "
                f"{expire_date_string}"
            )

            return {
                "valid": False,
                "reason": "invalid"
            }

        # ----------------------------------------------------
        # Hết hạn
        # ----------------------------------------------------

        if date.today() > expire_date:

            print(
                f"License expired: "
                f"{expire_date_string}"
            )

            return {
                "valid": False,
                "reason": "expired",
                "expire_date": expire_date_string
            }

        # ----------------------------------------------------
        # OK
        # ----------------------------------------------------

        print(
            f"License valid until: "
            f"{expire_date_string}"
        )

        return {
            "valid": True,
            "reason": None,
            "expire_date": expire_date_string,
            "data": license_data
        }

    def initialize_license(self):

        result = self.check_license()

        self.license_valid = result["valid"]

        self.license_reason = result.get(
            "reason"
        )

        if result["valid"]:

            self.license_data = result.get(
                "data"
            )

            expire_date_string = result.get(
                "expire_date"
            )
            expire_date = date.fromisoformat(
                expire_date_string
            )
            days_remaining = (
                expire_date - date.today()
            ).days

            if 0 <= days_remaining <= 15:
                self.license_status = (
                    f"Bản quyền đến {expire_date_string} "
                    f"còn {days_remaining} ngày"
                )
            else:
                self.license_status = None

            print(
                "License: VALID"
            )

        else:

            self.license_data = None
            self.license_status = None

            print(
                f"License: INVALID "
                f"({self.license_reason})"
            )

        return result

    # ========================================================
    # LICENSE NOTIFICATION
    # ========================================================

    def show_license_error(self, reason):

        if not self.icon:
            return

        if reason == "missing":

            self.icon.notify(
                "Không tìm thấy license.key.\n"
                "Vui lòng liên hệ nhà phát triển "
                "để được cấp license.",
                "HUB - Chưa có license"
            )

        elif reason == "expired":

            expire_date = ""

            if self.license_data:
                expire_date = self.license_data.get(
                    "expire_date",
                    ""
                )

            message = (
                "License đã hết hạn.\n"
                "Vui lòng liên hệ nhà phát triển "
                "để gia hạn."
            )

            if expire_date:
                message = (
                    f"License đã hết hạn "
                    f"({expire_date}).\n"
                    f"Vui lòng liên hệ nhà phát triển "
                    f"để gia hạn."
                )

            self.icon.notify(
                message,
                "HUB - License hết hạn"
            )

        else:

            self.icon.notify(
                "License không hợp lệ "
                "hoặc không thuộc máy này.",
                "HUB - License lỗi"
            )

    def show_license_expiring_notification(self):

        if not self.icon or not self.license_status:
            return

        self.icon.notify(
            f"{self.license_status}.\n"
            "Vui lòng liên hệ nhà phát triển để gia hạn.",
            "HUB - License sắp hết hạn"
        )

    # ========================================================
    # CHECK UI PERMISSION
    # ========================================================

    def can_use(self):

        if self.license_valid:
            return True

        self.show_license_error(
            self.license_reason or "invalid"
        )

        return False

    # ========================================================
    # ADMIN UI
    # ========================================================

    def open_admin_ui(
        self,
        icon,
        item
    ):

        # if not self.can_use():
        #     return

        webbrowser.open(
            f"http://{self.ip}:5173"
        )

    # ========================================================
    # USER UI
    # ========================================================

    def open_user_ui(
        self,
        icon,
        item
    ):

        # if not self.can_use():
        #     return

        if EDGE_PATH is None:

            self.icon.notify(
                "Không tìm thấy Microsoft Edge.",
                "HUB - Lỗi"
            )

            return

        try:

            settings_data = asyncio.run(
                open_settings()
            )

            self.ui = (
                settings_data
                .get("settings", {})
                .get("ui", "desktop")
            )

            url = (
                f"http://localhost:5174/"
                f"{self.ui}"
            )

            subprocess.Popen(
                [
                    str(EDGE_PATH),

                    "--kiosk",

                    url,

                    "--edge-kiosk-type=fullscreen",

                    "--no-first-run",

                    "--disable-session-crashed-bubble",
                ],

                cwd=BASE_DIR
            )

        except Exception as e:

            print(
                f"Failed to open user UI: {e}"
            )

            self.icon.notify(
                "Không thể mở giao diện "
                "người dùng.",
                "HUB - Lỗi"
            )

    # ========================================================
    # QUIT
    # ========================================================

    def quit(
        self,
        icon,
        item
    ):

        print("Stopping HUB...")

        self.set_status(
            self.STATUS_CLOSING
        )

        # Stop FastAPI
        self.server.should_exit = True

        # Stop tray
        icon.stop()

    # ========================================================
    # RUN
    # ========================================================

    def run(self):

        print("================================")
        print("Starting HUB Tray")
        print(f"BASE_DIR: {BASE_DIR}")
        print(
            f"license.key: "
            f"{self.get_license_path()}"
        )
        print("================================")

        # ----------------------------------------------------
        # Icon
        # ----------------------------------------------------

        icon_path = self.get_icon_path()

        image = Image.open(
            icon_path
        )

        # ----------------------------------------------------
        # Kiểm tra license trước khi dựng menu
        # ----------------------------------------------------

        result = self.initialize_license()

        # ----------------------------------------------------
        # Menu
        # ----------------------------------------------------
        menuItems = [
            MenuItem(
                "🛠    Mở giao diện quản trị",
                self.open_admin_ui
            ),

            pystray.Menu.SEPARATOR,

            MenuItem(
                "👤    Mở giao diện người dùng",
                self.open_user_ui
            ),

            pystray.Menu.SEPARATOR,

            MenuItem(
                self.status_label,
                None,
                enabled=False
            ),

            pystray.Menu.SEPARATOR,

            MenuItem(
                "⏻    Dừng",
                self.quit
            ),
        ] 
        if self.license_status:
            menuItems.insert(
                4,
                MenuItem(
                    f"⚠    {self.license_status}",
                    None,
                    enabled=False
                )
            )
        menu = pystray.Menu(
            *menuItems
        )

        # ----------------------------------------------------
        # Create tray
        # ----------------------------------------------------

        self.icon = pystray.Icon(
            "HUB",
            image,
            "HUB",
            menu
        )

        # ----------------------------------------------------
        # Notification sau khi tray đã chạy
        # ----------------------------------------------------

        if not result["valid"]:

            def notify_license_error():

                # Đợi tray initialize
                import time

                time.sleep(0.5)

                self.show_license_error(
                    result["reason"]
                )

            threading.Thread(
                target=notify_license_error,
                daemon=True
            ).start()

        else:

            self.set_running_status()

            if self.license_status:

                def notify_license_expiring():

                    import time

                    time.sleep(0.5)
                    self.show_license_expiring_notification()

                threading.Thread(
                    target=notify_license_expiring,
                    daemon=True
                ).start()

        # ----------------------------------------------------
        # Run tray
        # ----------------------------------------------------

        self.icon.run()

    # ========================================================
    # ICON PATH
    # ========================================================

    @staticmethod
    def get_icon_path():

        if getattr(
            sys,
            "frozen",
            False
        ):

            return os.path.join(
                sys._MEIPASS,
                "icon.ico"
            )

        return os.path.join(
            os.path.dirname(
                os.path.abspath(__file__)
            ),
            "icon.ico"
        )