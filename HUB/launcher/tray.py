import os
import sys
import webbrowser
import threading

import pystray
from PIL import Image
from pystray import MenuItem


class TrayApp:

    def __init__(self, server):
        self.server = server
        self.icon = None

    def open_admin_ui(self, icon, item):
        webbrowser.open("http://localhost:5173")

    def open_user_ui(self, icon, item):
        webbrowser.open("http://localhost:5174")

    def quit(self, icon, item):
        print("Stopping HUB...")

        # Stop FastAPI
        self.server.should_exit = True

        # Đóng tray
        icon.stop()

    def run(self):
        icon_path = self.get_icon_path()

        image = Image.open(icon_path)

        menu = pystray.Menu(
            MenuItem(
                "Mở giao diện quản trị",
                self.open_admin_ui
            ),
            MenuItem(
                "Mở giao diện người dùng",
                self.open_user_ui
            ),
            MenuItem(
                "Dừng",
                self.quit
            )
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