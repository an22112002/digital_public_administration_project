import asyncio
import json
from pywinauto import Desktop
import webview
from pathlib import Path

TITLE = "VNeID"

class SupportApi:

    def __init__(self):
        self.dlg = None
        self.window = None

    def destroy(self):
        if webview.windows:
            webview.windows[0].destroy()
        return True

    def upload_file(self, file_path):
        print("Python start")
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

    def close_window(self):
        if self.window:
            self.window.destroy()
        return True

    def log(self, *args):
        print("[JS]", *args)
        return True


api = SupportApi()

# url = "https://dichvucongnganhtuphap.moj.gov.vn/danh-sach-thu-tuc?vneid=1&MaTTHCDP=2.001019&MaTTHC=2.001019&MaCoQuanThucHien=H26.107&keyword="
# url = "https://dichvucongnganhtuphap.moj.gov.vn/danh-sach-thu-tuc?vneid=1&MaTTHCDP=2.001035&MaTTHC=2.001035&MaCoQuanThucHien=H26.107&keyword="
url = "https://dichvucongnganhtuphap.moj.gov.vn/danh-sach-thu-tuc?vneid=1&MaTTHCDP=1.000894&MaTTHC=1.000894&MaCoQuanThucHien=H26.107&keyword="
# url = "https://dichvucongnganhtuphap.moj.gov.vn/danh-sach-thu-tuc?vneid=1&MaCoQuanThucHien=H26.107&maThuTuc=1.001193"
# url = 'https://dichvucongnganhtuphap.moj.gov.vn/nop-ho-so/144264?vneid=1&tinhThanhId=1&maThuTuc=2.001019&MaDVC=2.001019.01'

paper_input = [
    {
        "name": "Bản chính hoặc bản sao có chứng thực hoặc bản sao điện tử được chứng thực từ bản chính của giấy chứng nhận quyền sở hữu, quyền sử dụng hoặc giấy tờ thay thế được pháp luật quy định đối với tài sản mà pháp luật quy định phải đăng ký quyền sở hữu, quyền sử dụng trong trường hợp giao dịch liên quan đến tài sản đó; trừ trường hợp người lập di chúc đang bị cái chết đe dọa đến tính mạng. Trường hợp nộp hồ sơ trực tiếp, người yêu cầu chứng thực có thể nộp bản sao kèm xuất trình bản chính để đối chiếu.",
        "file": r"D:\test\test.pdf",
        "type": "Chứng thực điện tử & giấy"
    },
    {
        "name": "Dự thảo giao dịch",
        "file": r"D:\test\test2.pdf",
        "type": "Chứng thực điện tử & giấy"
    },
    {
        "name": "CCCD",
        "file": r"D:\test\test3.pdf",
        "type": "Chứng thực điện tử & giấy"
    },
]

def btnNopHoSoClick():
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

def btnXacNhanClick():
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

def addTools():
    window.evaluate_js("""
    (() => {
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

def tableInsert():
    js_path = Path(__file__).parent / "js" / "table_insert.js"

    js = js_path.read_text(encoding="utf-8")

    papers_json = json.dumps(paper_input, ensure_ascii=False)

    js = js.replace("PAPERS_DATA", papers_json)

    window.evaluate_js(js)
    
window = webview.create_window(
    title=TITLE,
    url=url,
    fullscreen=True,
    js_api=api
)

window.events.loaded += lambda: addTools()

window.events.loaded += lambda: btnNopHoSoClick()
window.events.loaded += lambda: btnXacNhanClick()
window.events.loaded += lambda: tableInsert()

webview.start()