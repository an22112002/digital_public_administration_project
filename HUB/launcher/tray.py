import os
import sys
import webbrowser
from backend.config import open_settings

import pystray
from PIL import Image
from pystray import MenuItem
import asyncio


class TrayApp:

    STATUS_STARTING = "Đang khởi động"
    STATUS_RUNNING = "Đang chạy"
    STATUS_CLOSING = "Đang đóng"

    def __init__(self, server):
        self.server = server
        self.icon = None
        self.ip = "localhost"
        self.status = self.STATUS_STARTING

    def set_status(self, status):
        self.status = status
        if self.icon:
            self.icon.update_menu()

    def status_label(self, item):
        return f"Trạng thái: {self.status}"

    def open_admin_ui(self, icon, item):
        webbrowser.open(
            f"http://{self.ip}:5173"
        )

    def open_user_ui(self, icon, item):
        settings_data = asyncio.run(open_settings())

        self.ui = settings_data.get("settings", {}).get("ui", "desktop")

        webbrowser.open(
            f"http://{self.ip}:5174/{self.ui}"
        )

    def quit(self, icon, item):
        print("Stopping HUB...")
        self.set_status(self.STATUS_CLOSING)

        # Stop FastAPI
        self.server.should_exit = True

        # Đóng tray
        icon.stop()

    def run(self):
        icon_path = self.get_icon_path()

        image = Image.open(icon_path)

        menu = pystray.Menu(
            MenuItem("🛠    Mở giao diện quản trị", self.open_admin_ui),
            pystray.Menu.SEPARATOR,
            MenuItem("👤    Mở giao diện người dùng", self.open_user_ui),
            pystray.Menu.SEPARATOR,
            MenuItem(self.status_label, None, enabled=False),
            pystray.Menu.SEPARATOR,
            MenuItem("⏻    Dừng", self.quit),
        )

        self.icon = pystray.Icon(
            "HUB",
            image,
            "HUB",
            menu
        )

        self.icon.run()

    @staticmethod
    def get_icon_path():
        if getattr(sys, "frozen", False):
            return os.path.join(
                sys._MEIPASS,
                "icon.ico"
            )

        return os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "icon.ico"
        )