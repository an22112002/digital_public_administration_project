import asyncio
import json
from pywinauto import Desktop
import webview
from pathlib import Path
from typing import Literal
from form_auto_insert import *
import threading

TITLE = "VNeID"

PROCESSES = Literal["auto_pass_select_service", "insert_file_table", "form_dangKyKetHon"]

class DataProcess:

    def __init__(self, task_name: PROCESSES, data: list[dict]):
        self.task_name = task_name
        self.data = data

    def set_task_name(self, task_name: PROCESSES):
        self.task_name = task_name

    def set_data(self, data: list[dict]):
        self.data = data


# lớp SupportApi được sử dụng để hỗ trợ các chức năng liên quan đến giao diện người dùng trong ứng dụng webview. Nó cung cấp các phương thức để tương tác với cửa sổ webview, xử lý việc tải tệp và đóng cửa sổ.
class SupportApi:

    def __init__(self):
        self.window = None
        self.fill_form = False
        self.fill_form_lock = threading.Lock()

    def destroy(self):
        if webview.windows:
            webview.windows[0].destroy()
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
                # print("Desktop windows:", [w.window_text() for w in desktop.windows()])

                browser = desktop.window(title=TITLE)
                # print("Browser window:", browser.window_text())

                dialogs = [
                    w for w in browser.descendants(control_type="Window")
                    if w.window_text().strip() == "Open"
                ]

                if dialogs:
                    open_dialog = dialogs[-1]
                    # print("Found Open dialog:", open_dialog.window_text())
                    break
                else:
                    open_dialog = None

            except Exception as e:
                print("Find dialog error:", e)

        if open_dialog is None:
            raise RuntimeError("Không tìm thấy dialog Open")

        # =========================
        # File name
        # =========================

        edit = None

        for e in open_dialog.descendants(control_type="Edit"):
            try:
                # print(
                #     "EDIT:",
                #     repr(e.window_text()),
                #     "automation_id:",
                #     e.element_info.automation_id
                # )

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
                    # print(
                    #     "BUTTON:",
                    #     repr(b.window_text()),
                    #     "automation_id:",
                    #     b.element_info.automation_id
                    # )

                    if b.window_text().strip() == "Open" and b.element_info.automation_id == "1":
                        button = b
                        break

                except Exception:
                    pass

        if button is None:
            raise RuntimeError("Không tìm thấy nút Open")

        button.click_input()

        print("Python end")

        return True

    # điền form
    def form_fill(self, form_data, form_type):
        if not self.fill_form_lock.acquire(blocking=False):
            print("[PY] FORM FILL ALREADY RUNNING -> SKIP")
            return False
        try:
            if self.fill_form:
                print("[PY] FORM ALREADY DONE -> SKIP")
                return False
            self.fill_form = True
            print("[PY] ===== FORM INSERT START =====")
            asyncio.run(self._form_fill(form_data, form_type))
            print("[PY] ===== FORM INSERT DONE =====")
            return True

        except Exception as e:
            print("[PY] FORM INSERT ERROR:", e)
            # cho phép retry nếu fill thất bại
            self.fill_form = False
            raise
        finally:
            self.fill_form_lock.release()
 
    async def _form_fill(self, form_data, form_type:str):
        if form_type == "form_dangKyKetHon":
            await formDangKyKetHonInsert(form_data)

        return True

    def close_window(self):
        self.destroy()
        return True

    def log(self, *args):
        print("[JS]", *args)
        return True

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
        const timer = setInterval(() => {
            const btn = [...document.querySelectorAll("button")]
                .find(b => b.textContent.trim() === "Xác nhận");

            if (btn) {
                btn.click();
                clearInterval(timer);
            }
        }, 1000);
    })();
    """)

# hàm thêm các công cụ hỗ trợ vào giao diện webview, bao gồm nút Reload và nút Close. 
# Nút Reload sẽ tải lại trang web hiện tại, trong khi nút Close sẽ đóng cửa sổ webview.
def addTools(window):
    window.evaluate_js("""
    (() => {
        if (document.getElementById("pywebview-tools")) {
            clearInterval(timer);
            return;
        }
        const timer = setInterval(() => {

            if (!document.body) {
                return;
            }

            if (document.getElementById("pywebview-tools")) {
                clearInterval(timer);
                return;
            }

            clearInterval(timer);

            const tools = document.createElement("div");
            tools.id = "pywebview-tools";

            Object.assign(tools.style, {
                position: "fixed",
                top: "10px",
                right: "10px",
                zIndex: "999999",
                backgroundColor: "#fff",
                padding: "8px",
                border: "1px solid #ccc",
                borderRadius: "6px",
                display: "flex",
                gap: "6px",
                boxShadow: "0 2px 8px rgba(0,0,0,0.15)"
            });

            const btnReload = document.createElement("button");
            btnReload.textContent = "Reload";

            btnReload.onclick = () => {
                window.location.reload();
            };

            const btnClose = document.createElement("button");
            btnClose.textContent = "Close";

            btnClose.onclick = () => {
                window.pywebview.api.destroy();
            };

            tools.appendChild(btnReload);
            tools.appendChild(btnClose);

            document.body.appendChild(tools);

        }, 100);
    })();
    """)

# ------------------- các hàm gốc từ js ngoài --------------------
# tự động tìm dịch vụ công phù hợp với tỉnh, xã
def autoPassSelectService(window, data: dict):
    js_path = Path(__file__).parent / "js" / "auto_pass_select_service.js"

    js = js_path.read_text(encoding="utf-8")

    service_name = data.get("service_name")
    province = data.get("province")
    commune = data.get("commune")

    js = js.replace("SERVICE_NAME", json.dumps(service_name, ensure_ascii=False))
    js = js.replace("PROVINCE", json.dumps(province, ensure_ascii=False))
    js = js.replace("COMMUNE", json.dumps(commune, ensure_ascii=False))
    js = js.replace("SERVICE_POSITION", json.dumps(data.get("service_position", 1), ensure_ascii=False))
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
    api = SupportApi()
        
    window = webview.create_window(
        title=TITLE,
        url=url,
        fullscreen=True,
        js_api=api
    )

    window.events.loaded += lambda: on_loaded(window, data_process)

    webview.start()

def on_loaded(window, data_process: list[DataProcess]):
    # Thêm công cụ hỗ trợ vào giao diện webview
    addTools(window)

    # tự động ấn nút Nộp hồ sơ và Xác nhận khi trang web được tải xong
    # btnNopHoSoClick(window)
    btnXacNhanClick(window)

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
    # url = "https://dichvucongnganhtuphap.moj.gov.vn/danh-sach-thu-tuc?vneid=1&MaTTHCDP=2.001035&MaTTHC=2.001035&MaCoQuanThucHien=H26.107&keyword="

    # paper_input = [
    #     {
    #         "name": "Bản chính hoặc bản sao có chứng thực hoặc bản sao điện tử được chứng thực từ bản chính của giấy chứng nhận quyền sở hữu, quyền sử dụng hoặc giấy tờ thay thế được pháp luật quy định đối với tài sản mà pháp luật quy định phải đăng ký quyền sở hữu, quyền sử dụng trong trường hợp giao dịch liên quan đến tài sản đó; trừ trường hợp người lập di chúc đang bị cái chết đe dọa đến tính mạng. Trường hợp nộp hồ sơ trực tiếp, người yêu cầu chứng thực có thể nộp bản sao kèm xuất trình bản chính để đối chiếu.",
    #         "file": r"D:\test\test.pdf",
    #         "type": "Chứng thực điện tử & giấy"
    #     },
    #     {
    #         "name": "Dự thảo giao dịch",
    #         "file": r"D:\test\test2.pdf",
    #         "type": "Chứng thực điện tử & giấy"
    #     },
    #     {
    #         "name": "CCCD",
    #         "file": r"D:\test\test3.pdf",
    #         "type": "Chứng thực điện tử & giấy"
    #     },
    # ]

    # data_process = [
    #     DataProcess(task_name="insert_file_table", data=paper_input)
    # ]

    # Đăng ký kết hôn
    # url = "https://dichvucongnganhtuphap.moj.gov.vn/danh-sach-thu-tuc?vneid=1&MaTTHCDP=1.000894&MaTTHC=1.000894&MaCoQuanThucHien=H26.107&keyword="
    # url = "https://dichvucong.gov.vn/dvc-dich-vu-cong-truc-tuyen"
    url = "https://dichvucong.gov.vn/tim-kiem-thu-tuc-hanh-chinh?formalityId=019d2bfd-3fac-7489-b53b-a15eb239a6fe&formalityCaseId=019d4346-42c5-71a1-9328-f59faac00421"

    province = "Thành phố Hà Nội"
    commune = "Phường Ba Đình"

    data_auto_pass = {
        "service_name": "Thủ tục đăng ký kết hôn",
        "province": province,
        "commune": commune,
        "button_send_documents_position": 1
    }

    form_input = [
        {
            "type": "husband",
            "fullname": "Nguyễn Văn A",
            "dob": "01011999",
            "sex": "Nam",
            "CCCD_id": "123456789",
            "issue_date": "01012020",
            "address": "123 Đường ABC, Quận XYZ, TP.HCM",
        },
        {
            "type": "wife",
            "fullname": "Trần Thị B",
            "dob": "02021992",
            "sex": "Nữ",
            "CCCD_id": "987654321",
            "issue_date": "02022020",
            "address": "456 Đường DEF, Quận UVW, TP.HCM",
        }
    ]

    paper_input = [
        {
            "name": "- Mẫu hộ tịch điện tử tương tác đăng ký kết hôn (do người yêu cầu cung cấp thông tin theo hướng dẫn trên Cổng dịch vụ công, nếu người có yêu cầu lựa chọn nộp hồ sơ theo hình thức trực tuyến)",
            "file": "",
            "type": "Chứng thực điện tử & giấy"
        },
        {
            "name": "- Hộ chiếu/Chứng minh nhân dân/Thẻ căn cước công dân/Thẻ căn cước/Căn cước điện tử/Giấy chứng nhận căn cước hoặc các giấy tờ khác có dán ảnh và thông tin cá nhân do cơ quan có thẩm quyền cấp, còn giá trị sử dụng để chứng minh về nhân thân của cả hai bên có yêu cầu đăng ký lại kết hôn. Trường hợp các thông tin cá nhân trong các giấy tờ này đã có trong CSDLQGVDC, CSDLHTĐT, được hệ thống điền tự động thì không phải tải lên (theo hình thức trực tuyến).",
            "file": r"D:\test\test2.pdf",
            "type": "Chứng thực điện tử & giấy"
        },
        {
            "name": "- Giấy tờ có giá trị chứng minh thông tin về cư trú trong trường hợp cơ quan đăng ký hộ tịch không thể khai thác được thông tin về nơi cư trú của công dân theo các phương thức quy định tại khoản 2 Điều 14 Nghị định số 104/2022/NĐ-CP ngày 21/12/2022 của Chính phủ. Trường hợp các thông tin về giấy tờ chứng minh nơi cư trú đã được khai thác từ Cơ sở dữ liệu quốc gia về dân cư bằng các phương thức này thì người có yêu cầu không phải xuất trình (theo hình thức trực tiếp) hoặc tải lên (theo hình thức trực tuyến).",
            "file": r"D:\test\test3.pdf",
            "type": "Chứng thực điện tử & giấy"
        },
    ]

    data_process = [
        DataProcess(task_name="auto_pass_select_service", data=data_auto_pass),
        DataProcess(task_name="insert_file_table", data=paper_input),
        DataProcess(task_name="form_dangKyKetHon", data=form_input)
    ]

    process_with_webview(url, data_process)