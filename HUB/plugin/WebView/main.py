import asyncio
import json
from pywinauto import Desktop
import webview
from pathlib import Path
from typing import Literal
from plugin.WebView.forms.form_dangKyKetHon import formDangKyKetHonInsert
from plugin.WebView.forms.form_caiChinhHoTich import formCaiChinhHoTichInsert
from plugin.WebView.forms.form_xacNhanTinhTrangHonNhan import formXacNhanTinhTrangHonNhanInsert
import threading
import os
import win32gui
import win32con
import win32api
import win32process
import ctypes
import time

PROCESSES = Literal["auto_pass_select_service", "insert_file_table", "form_dangKyKetHon", "form_caiChinhHoTich", "form_xacNhanTinhTrangHonNhan"]

TITLE = "VNeID"

class DataProcess:

    def __init__(self, task_name: PROCESSES, data: list[dict]):
        self.task_name = task_name
        self.data = data

    def print_out(self):
        print(f"DataProcess: task_name={self.task_name}, data={self.data}")

    def set_task_name(self, task_name: PROCESSES):
        self.task_name = task_name

    def set_data(self, data: list[dict]):
        self.data = data

    def to_dict(self) -> dict:
        return {
            "task_name": self.task_name,
            "data": self.data
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            task_name=data["task_name"],
            data=data["data"]
        )

# lớp SupportApi được sử dụng để hỗ trợ các chức năng liên quan đến giao diện người dùng trong ứng dụng webview. Nó cung cấp các phương thức để tương tác với cửa sổ webview, xử lý việc tải tệp và đóng cửa sổ.
class SupportApi:

    def __init__(self, debug=False):
        self.window = None
        self.fill_form = False
        self.fill_form_lock = threading.Lock()
        self.debug = debug

    def destroy(self):
        try:
            if webview.windows:
                for window in webview.windows:
                    window.destroy()
        except Exception as e:
            if self.debug:
                print("[PY] Destroy WebView error:", e)

        return True

    # tải lên file tài liệu
    def upload_file(self, file_path):
        return asyncio.run(self._upload_file(file_path))

    async def _upload_file(self, file_path):

        # =========================
        # Wait Open dialog
        # =========================

        open_dialog = None

        for _ in range(200):

            try:
                desktop = Desktop(backend="uia")
                if self.debug:
                    print("Desktop windows:", [w.window_text() for w in desktop.windows()])

                browser = desktop.window(title=TITLE)
                if self.debug:
                    print("Browser window:", browser.window_text())

                dialogs = [
                    w for w in browser.descendants(control_type="Window")
                    if w.window_text().strip() == "Open"
                ]

                if dialogs:
                    open_dialog = dialogs[-1]
                    if self.debug:
                        print("Found Open dialog:", open_dialog.window_text())
                    break
                else:
                    open_dialog = None

            except Exception as e:
                if self.debug:
                    print("Find dialog error:", e)

        if open_dialog is None:
            raise RuntimeError("Không tìm thấy dialog Open")

        # =========================
        # File name
        # =========================

        edit = None

        for e in open_dialog.descendants(control_type="Edit"):
            try:
                if self.debug:
                    print(
                        "EDIT:",
                        repr(e.window_text()),
                        "automation_id:",
                        e.element_info.automation_id
                    )

                if e.element_info.automation_id == "1148":
                    edit = e
                    break

            except Exception:
                pass

        if edit is None:
            raise RuntimeError("Không tìm thấy ô File name")

        edit.click_input()
        edit.type_keys("^a")
        edit.set_edit_text(file_path)
        # edit.type_keys(file_path, with_spaces=True)

        # =========================
        # Open button
        # =========================

        button = None
        control_type = ["Button", "SplitButton"]
        for ct in control_type:
            for b in open_dialog.descendants(control_type=ct):
                try:
                    if self.debug:
                        print(
                            "BUTTON:",
                            repr(b.window_text()),
                            "automation_id:",
                            b.element_info.automation_id
                        )

                    if b.window_text().strip() == "Open" and b.element_info.automation_id == "1":
                        button = b
                        break

                except Exception:
                    pass

        if button is None:
            raise RuntimeError("Không tìm thấy nút Open")

        button.click_input()

        if self.debug:
            print("Python end")

        return True

    # điền form
    def form_fill(self, form_data, form_type):
        if not self.fill_form_lock.acquire(blocking=False):
            if self.debug:
                print("[PY] FORM FILL ALREADY RUNNING -> SKIP")
            return False
        try:
            if self.fill_form:
                if self.debug:
                    print("[PY] FORM ALREADY DONE -> SKIP")
                return False
            self.fill_form = True
            if self.debug:
                print("[PY] ===== FORM INSERT START =====")
            asyncio.run(self._form_fill(form_data, form_type))
            if self.debug:
                print("[PY] ===== FORM INSERT DONE =====")
            return True

        except Exception as e:
            if self.debug:
                print("[PY] FORM INSERT ERROR:", e)
            # cho phép retry nếu fill thất bại
            self.fill_form = False
            raise
        finally:
            self.fill_form_lock.release()

    # UPDATE: thêm tham số form_type để xác định loại form cần điền
    async def _form_fill(self, form_data, form_type:str):
        if form_type == "form_dangKyKetHon":
            await formDangKyKetHonInsert(form_data)
        elif form_type == "form_caiChinhHoTich":
            await formCaiChinhHoTichInsert(form_data)
        elif form_type == "form_xacNhanTinhTrangHonNhan":
            await formXacNhanTinhTrangHonNhanInsert(form_data)

        return True

    def close_window(self):
        self.destroy()
        return True

    def log(self, *args):
        if self.debug:
            print("[JS]", *args)
        return True


def focus_window(title: str):
    hwnd = win32gui.FindWindow(None, title)

    if not hwnd:
        print(f"[WEBVIEW] Cannot find window: {title}")
        return

    print(f"[WEBVIEW] HWND={hwnd}")

    # Restore nếu đang minimize
    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)

    # Thread sở hữu WebView
    target_thread_id, _ = win32process.GetWindowThreadProcessId(hwnd)

    # Thread đang giữ foreground
    foreground_hwnd = win32gui.GetForegroundWindow()

    if foreground_hwnd:
        foreground_thread_id, _ = (
            win32process.GetWindowThreadProcessId(
                foreground_hwnd
            )
        )
    else:
        foreground_thread_id = 0

    current_thread_id = win32api.GetCurrentThreadId()

    attached = False

    try:
        # Attach current thread với foreground thread
        if (
            foreground_thread_id
            and foreground_thread_id != current_thread_id
        ):
            ctypes.windll.user32.AttachThreadInput(
                current_thread_id,
                foreground_thread_id,
                True
            )
            attached = True

        # Attach current thread với thread của WebView
        if target_thread_id != current_thread_id:
            ctypes.windll.user32.AttachThreadInput(
                current_thread_id,
                target_thread_id,
                True
            )

        # Activate / foreground
        win32gui.BringWindowToTop(hwnd)
        win32gui.ShowWindow(hwnd, win32con.SW_SHOW)
        win32gui.SetForegroundWindow(hwnd)

        print("[WEBVIEW] Window focused")

    except Exception as e:
        print(f"[WEBVIEW] Focus error: {e}")

    finally:
        if target_thread_id != current_thread_id:
            ctypes.windll.user32.AttachThreadInput(
                current_thread_id,
                target_thread_id,
                False
            )

        if attached:
            ctypes.windll.user32.AttachThreadInput(
                current_thread_id,
                foreground_thread_id,
                False
            )

# tự động ấn nút Nộp hồ sơ
def btnNopHoSoClick(window):
    window.evaluate_js("""
    (() => {
        const timer = setInterval(() => {
            const btn = [...document.querySelectorAll("button")]
                .find(b => b.textContent.trim() === "Nộp hồ sơ");

            if (btn) {
                btn.click();
                clearInterval(timer);
            }
        }, 1000);
    })();
    """)

# tự động ấn nút Xác nhận
def btnXacNhanClick(window):
    window.evaluate_js("""
    (() => {
        if (window.__xacNhanTimer) {
            clearInterval(window.__xacNhanTimer);
        }

        window.__xacNhanTimer = setInterval(() => {
            const btn = [...document.querySelectorAll("button")]
                .find(b => b.textContent.trim() === "Xác nhận");

            if (btn) {
                console.log("[AUTO] Click Xác nhận");

                clearInterval(window.__xacNhanTimer);
                window.__xacNhanTimer = null;

                btn.click();
            }
        }, 500);

        setTimeout(() => {
            if (window.__xacNhanTimer) {
                clearInterval(window.__xacNhanTimer);
                window.__xacNhanTimer = null;

                console.log("[AUTO] Timeout: không tìm thấy Xác nhận");
            }
        }, 30000);

        return true;
    })();
    """)

# thoothoogobsa nếu có text: can't reach this page, tạo box nhỏ top left để thông báo hãy chờ
def checkCantReachThisPage(window):
    window.evaluate_js("""
    (() => {
        const content = document.body.textContent || "";
        if (content.includes("can't reach this page")) {
            const box = document.createElement("div");
            box.style.position = "fixed";
            box.style.width = "400px";
            box.style.height = "auto";
            box.style.top = "10px";
            box.style.left = "10px";
            box.style.backgroundColor = "white";
            box.style.color = "black";
            box.style.padding = "10px";
            box.style.zIndex = "9999";
            box.textContent = "Không thể truy cập trang web. Web Dịch Vụ Công có thể đang có quá nhiều truy cập. Vui lòng chờ hoặc thử reload lại trang. Việc mất kết nối có thể mất vài phút để tự khôi phục.";
            document.body.appendChild(box);
        }
        return true;
    })();
    """)

# hàm thêm các công cụ hỗ trợ vào giao diện webview, bao gồm nút Reload và nút Close. 
# Nút Reload sẽ tải lại trang web hiện tại, trong khi nút Close sẽ đóng cửa sổ webview.
def addTools(window):
    js_path = Path(__file__).parent / "js" / "tools.js"
    
    js = js_path.read_text(encoding="utf-8")

    window.evaluate_js(js)

# ------------------- các hàm gốc từ js ngoài --------------------
# tự động tìm dịch vụ công phù hợp với tỉnh, xã
def autoPassSelectService(window, data: dict):
    js_path = Path(__file__).parent / "js" / "auto_pass_select_service.js"

    js = js_path.read_text(encoding="utf-8")

    province = data.get("province")
    commune = data.get("commune")

    js = js.replace("PROVINCE", json.dumps(province, ensure_ascii=False))
    js = js.replace("COMMUNE", json.dumps(commune, ensure_ascii=False))
    js = js.replace("BUTTON_SEND_DOCUMENTS_POSITION", json.dumps(data.get("button_send_documents_position", 1), ensure_ascii=False))

    window.evaluate_js(js)

# nhập dữ liệu giấy tờ vào bảng trong giao diện webview
def fileTableInsert(window, paper_input):
    js_path = Path(__file__).parent / "js" / "table_insert.js"

    js = js_path.read_text(encoding="utf-8")

    papers_json = json.dumps(paper_input, ensure_ascii=False)

    js = js.replace("PAPERS_DATA", papers_json)

    window.evaluate_js(js)

# nhập form đăng ký kết hôn vào giao diện webview
def formInsert(window, form_data, form_type: str):

    js_path = Path(__file__).parent / "js" / "form_trigger.js"

    js = js_path.read_text(encoding="utf-8")

    form_data_json = json.dumps(
        form_data,
        ensure_ascii=False
    )

    form_type_json = json.dumps(
        form_type,
        ensure_ascii=False
    )

    js = js.replace("FORM_DATA", form_data_json)
    js = js.replace("FORM_TYPE", form_type_json)

    window.evaluate_js(js)

# hàm xử lý chính
# url: URL của trang web cần hiển thị trong webview.
# paper_input: dữ liệu đầu vào liên quan đến các giấy tờ cần xử lý
def process_with_webview(url: str, data_process: list[DataProcess]):
    print(
        f"[WEBVIEW PROCESS] PID={os.getpid()} START"
    )
    api = SupportApi()
        
    window = webview.create_window(
        title=TITLE,
        url=url,
        fullscreen=True,
        js_api=api
    )

    window.events.loaded += lambda: on_loaded(window, data_process)

    def on_window_shown():
        print(
            f"[WEBVIEW PROCESS] PID={os.getpid()} "
            "WINDOW SHOWN"
        )

        time.sleep(0.2)

        focus_window(TITLE)

    window.events.shown += on_window_shown

    print(
        f"[WEBVIEW PROCESS] PID={os.getpid()} "
        "calling webview.start()"
    )

    def on_window_closed():
        print(
            f"[WEBVIEW PROCESS] PID={os.getpid()} "
            "WINDOW CLOSED"
        )

    window.events.closed += on_window_closed

    print(
        f"[WEBVIEW PROCESS] PID={os.getpid()} "
        f"calling webview.start()"
    )

    webview.start()

    print(
        f"[WEBVIEW PROCESS] PID={os.getpid()} "
        f"webview.start() returned"
    )

def on_loaded(window, data_process: list[DataProcess]):
    # Thêm công cụ hỗ trợ vào giao diện webview
    addTools(window)

    # tự động ấn nút Nộp hồ sơ và Xác nhận khi trang web được tải xong
    # btnNopHoSoClick(window)
    btnXacNhanClick(window)

    checkCantReachThisPage(window)

    for process in data_process:
        if process.task_name == "auto_pass_select_service":
            print("[PY] Auto pass select service:")
            autoPassSelectService(window, process.data)
        elif process.task_name == "insert_file_table":
            print("[PY] Insert file table:")
            fileTableInsert(window, process.data)
        elif process.task_name.startswith("form"):
            print("[PY] Form insert:")
            formInsert(window, process.data, process.task_name)

if __name__ == "__main__":
    # ví dụ sử dụng

    # Chứng thực hợp đồng
    url = "https://dichvucong.gov.vn/tim-kiem-thu-tuc-hanh-chinh?formalityId=019d2bfd-95fa-70ca-93fd-4cab11b87897&formalityCaseId=019db06b-1e13-773f-bd01-af4904294075"

    province = "Thành phố Hà Nội"
    commune = "Phường Ba Đình"

    data_auto_pass = {
        "province": province,
        "commune": commune,
        "button_send_documents_position": 1
    }

    paper_input = [
        {
            "name": "Bản chính hoặc bản sao có chứng thực hoặc bản sao điện tử được chứng thực từ bản chính của giấy chứng nhận quyền sở hữu, quyền sử dụng hoặc giấy tờ thay thế được pháp luật quy định đối với tài sản mà pháp luật quy định phải đăng ký quyền sở hữu, quyền sử dụng trong trường hợp giao dịch liên quan đến tài sản đó; trừ trường hợp người lập di chúc đang bị cái chết đe dọa đến tính mạng. Trường hợp nộp hồ sơ trực tiếp, người yêu cầu chứng thực có thể nộp bản sao kèm xuất trình bản chính để đối chiếu.",
            "file": r"D:\test\test.pdf"
        },
        {
            "name": "Dự thảo giao dịch",
            "file": r"D:\test\test2.pdf"
        },
        {
            "name": "CCCD",
            "file": r"D:\test\test3.pdf"
        },
    ]

    data_process = [
        DataProcess(task_name="auto_pass_select_service", data=data_auto_pass),
        DataProcess(task_name="insert_file_table", data=paper_input)
    ]

    # Đăng ký kết hôn
    # url = "https://dichvucongnganhtuphap.moj.gov.vn/danh-sach-thu-tuc?vneid=1&MaTTHCDP=1.000894&MaTTHC=1.000894&MaCoQuanThucHien=H26.107&keyword="
    # url = "https://dichvucong.gov.vn/dvc-dich-vu-cong-truc-tuyen"
    # url = "https://dichvucong.gov.vn/tim-kiem-thu-tuc-hanh-chinh?formalityId=019d2bfd-3fac-7489-b53b-a15eb239a6fe&formalityCaseId=019d4346-42c5-71a1-9328-f59faac00421"

    # province = "Thành phố Hà Nội"
    # commune = "Phường Ba Đình"

    # data_auto_pass = {
    #     "service_name": "Thủ tục đăng ký kết hôn",
    #     "province": province,
    #     "commune": commune,
    #     "button_send_documents_position": 1
    # }
    # # OCR output
    # form_input = [
    #     {
    #         "type": "husband",
    #         "fullname": "Nguyễn Văn A",
    #         "dob": "01011999",
    #         "sex": "Nam",
    #         "CCCD_id": "123456789",
    #         "issue_date": "01012020",
    #         "address": "123 Đường ABC, Quận XYZ, TP.HCM",
    #     },
    #     {
    #         "type": "wife",
    #         "fullname": "Trần Thị B",
    #         "dob": "02021992",
    #         "sex": "Nữ",
    #         "CCCD_id": "987654321",
    #         "issue_date": "02022020",
    #         "address": "456 Đường DEF, Quận UVW, TP.HCM",
    #     }
    # ]

    # paper_input = [
    #     {
    #         "name": "- Mẫu hộ tịch điện tử tương tác đăng ký kết hôn (do người yêu cầu cung cấp thông tin theo hướng dẫn trên Cổng dịch vụ công, nếu người có yêu cầu lựa chọn nộp hồ sơ theo hình thức trực tuyến)",
    #         "file": "",
    #         "type": "Chứng thực điện tử & giấy"
    #     },
    #     {
    #         "name": "- Hộ chiếu/Chứng minh nhân dân/Thẻ căn cước công dân/Thẻ căn cước/Căn cước điện tử/Giấy chứng nhận căn cước hoặc các giấy tờ khác có dán ảnh và thông tin cá nhân do cơ quan có thẩm quyền cấp, còn giá trị sử dụng để chứng minh về nhân thân của cả hai bên có yêu cầu đăng ký lại kết hôn. Trường hợp các thông tin cá nhân trong các giấy tờ này đã có trong CSDLQGVDC, CSDLHTĐT, được hệ thống điền tự động thì không phải tải lên (theo hình thức trực tuyến).",
    #         "file": r"D:\test\test2.pdf",
    #         "type": "Chứng thực điện tử & giấy"
    #     },
    #     {
    #         "name": "- Giấy tờ có giá trị chứng minh thông tin về cư trú trong trường hợp cơ quan đăng ký hộ tịch không thể khai thác được thông tin về nơi cư trú của công dân theo các phương thức quy định tại khoản 2 Điều 14 Nghị định số 104/2022/NĐ-CP ngày 21/12/2022 của Chính phủ. Trường hợp các thông tin về giấy tờ chứng minh nơi cư trú đã được khai thác từ Cơ sở dữ liệu quốc gia về dân cư bằng các phương thức này thì người có yêu cầu không phải xuất trình (theo hình thức trực tiếp) hoặc tải lên (theo hình thức trực tuyến).",
    #         "file": r"D:\test\test3.pdf",
    #         "type": "Chứng thực điện tử & giấy"
    #     },
    # ]

    # data_process = [
    #     DataProcess(task_name="auto_pass_select_service", data=data_auto_pass),
    #     DataProcess(task_name="insert_file_table", data=paper_input),
    #     DataProcess(task_name="form_dangKyKetHon", data=form_input)
    # ]

    process_with_webview(url, data_process)