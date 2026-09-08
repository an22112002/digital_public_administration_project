from pywinauto import keyboard, mouse
from typing import Literal
import time
import pyperclip

def paste_text(text):
    pyperclip.copy(text)
    time.sleep(0.05)
    keyboard.send_keys("^v")

def is_edited() -> bool:
    time.sleep(0.05)

    keyboard.send_keys("{TAB}")
    time.sleep(0.05)

    # Giá trị đánh dấu trước khi Ctrl+C
    sentinel = "__HUB_CLIPBOARD_CHECK__"
    pyperclip.copy(sentinel)

    keyboard.send_keys("^c")
    time.sleep(0.1)

    content = pyperclip.paste()

    keyboard.send_keys("+{TAB}")
    time.sleep(0.05)

    # Nếu Ctrl+C không copy được gì,
    # clipboard vẫn là sentinel
    if content == sentinel:
        return False

    return content != ""

async def press_key(
    type: Literal["text", "tab", "checkbox", "select", "date"],
    value: str | int,
    passing: bool = False
) -> None:
    # print("[PY] Pressing key:", type, value)
    if type == "text":
        keyboard.send_keys("{TAB}")
        time.sleep(0.05)
        paste_text(str(value))
    elif type == "date":
        if is_edited():
            await press_key("tab", 3)
            time.sleep(0.05)
            keyboard.send_keys("{BACKSPACE}")
            time.sleep(0.05)
            keyboard.send_keys("+{TAB}")
            time.sleep(0.05)
            keyboard.send_keys("{BACKSPACE}")
            time.sleep(0.05)
            keyboard.send_keys("+{TAB}")
            time.sleep(0.05)
            keyboard.send_keys("{BACKSPACE}")
            time.sleep(0.05)
            keyboard.send_keys("+{TAB}")
            time.sleep(0.05)
        keyboard.send_keys("{TAB}")
        time.sleep(0.05)
        keyboard.send_keys(str(value))
    elif type == "tab":
        for _ in range(int(value)):
            keyboard.send_keys("{TAB}")
            time.sleep(0.05)
    elif type == "checkbox":
        keyboard.send_keys("{TAB}")
        time.sleep(0.05)
        keyboard.send_keys("{SPACE}")
    elif type == "select":
        keyboard.send_keys("{TAB}")
        time.sleep(0.05)
        keyboard.send_keys("{ENTER}")
        time.sleep(0.05)
        paste_text(str(value))
        time.sleep(0.05)
        keyboard.send_keys("{ENTER}")
    time.sleep(0.1)  # Thêm độ trễ để đảm bảo thao tác được thực hiện đúng

# đưa con trỏ về đầu form
async def reset():
    mouse.move(coords=(100, 500))  # Di chuyển chuột ra ngoài form
    time.sleep(0.05)
    mouse.click(button='left', coords=(100, 100))  # Click để đảm bảo form mất focus
    time.sleep(0.05)