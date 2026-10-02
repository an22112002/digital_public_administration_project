from pathlib import Path
from enum import Enum
import tkinter as tk
import twain
from io import BytesIO
from PIL import Image
import time

from backend.log.main import log_exception

class ScanTwainStatus(Enum):
    SUCCESS = "success"
    NO_DOCUMENT = "no_document"
    PAPER_JAM = "paper_jam"
    DEVICE_BUSY = "device_busy"
    DEVICE_OFFLINE = "device_offline"
    COMMUNICATION_ERROR = "communication_error"
    INVALID_DEVICE = "invalid_device"
    UNKNOWN_ERROR = "unknown_error"

# Lấy danh sách các thiết bị scanner được cài đặt trên hệ thống
async def get_list_scanner_devices() -> list:
    root = None
    try:
        root = tk.Tk()
        root.withdraw()
        with twain.SourceManager(root) as sm:
            return sm.source_list
    except Exception as e:
        log_exception(e, "SCANNER")
        print(f"[Scanner] Lỗi khi lấy danh sách thiết bị scanner: {e}")
        return []
    finally:
        if root is not None:
            try:
                root.destroy()
            except Exception:
                pass

# Scan toàn bộ giấy tờ sang folder JPEG
async def scan_documents_to_folder(
    timestamp: int,
    output_folder: str,
    filename: str,
    device_name: str,
) -> tuple[ScanTwainStatus, str | None]:
    try:
        root = None
        images = []

        output_folder_path = Path(output_folder) / f"patch_{timestamp}"
        output_folder_path.mkdir(parents=True, exist_ok=True)

        output_file = output_folder_path / f"{filename}.pdf"  # Tên tệp PDF đầu ra
        # ==================================================
        # MỞ SCANNER
        # ==================================================
        root = tk.Tk()
        root.withdraw()
        with twain.SourceManager(root) as sm:
            source = sm.open_source(device_name)

            if source is None:
                # Không thể mở máy scan.
                return (ScanTwainStatus.INVALID_DEVICE, None)

            # ==================================================
            # DPI 300
            # ==================================================

            try:
                source.set_capability(
                    twain.ICAP_XRESOLUTION,
                    twain.TWTY_FIX32,
                    300
                )

            except Exception as e:
                print(f"[Scanner] Không đặt được X DPI: {e}")

            try:
                source.set_capability(
                    twain.ICAP_YRESOLUTION,
                    twain.TWTY_FIX32,
                    300
                )

            except Exception as e:
                print(f"[Scanner] Không đặt được Y DPI: {e}")

            # ==================================================
            # COLOR
            # ==================================================

            try:
                source.set_capability(
                    twain.ICAP_PIXELTYPE,
                    twain.TWTY_UINT16,
                    twain.TWPT_RGB
                )

            except Exception as e:
                print(f"[Scanner] Không đặt được Color: {e}")

            # ==================================================
            # DUPLEX
            # ==================================================

            try:
                # Kiểm tra scanner có hỗ trợ duplex không
                _, duplex_value = source.get_capability(
                    twain.CAP_DUPLEX
                )

                # 0 = không hỗ trợ duplex
                # 1 = 1-pass duplex
                # 2 = 2-pass duplex
                if duplex_value != twain.TWDX_NONE:
                    source.set_capability(
                        twain.CAP_DUPLEXENABLED,
                        twain.TWTY_BOOL,
                        True
                    )

            except Exception as e:
                print(f"[Scanner] Không hỗ trợ hoặc không bật được duplex: {e}")

            # ==================================================
            # AUTO SCALE
            # ==================================================

            try:
                source.set_capability(
                    twain.ICAP_AUTOSIZE,
                    twain.TWTY_UINT16,
                    twain.TWAS_NONE
                )

            except Exception:
                print("[Scanner] Auto scale: không hỗ trợ -> bỏ qua")

            # ==================================================
            # BẮT ĐẦU SCAN
            # ==================================================

            source.request_acquire(
                show_ui=False,
                modal_ui=False
            )

            # ==================================================
            # NHẬN TỪNG TRANG
            # ==================================================

            page_number = 0

            start_time = time.time()

            while True:

                result = source.xfer_image_natively()

                if result:

                    handle, remaining_count = result

                    if handle is not None:

                        bmp_bytes = twain.dib_to_bm_file(handle)

                        if not bmp_bytes:
                            break

                        try:
                            image = Image.open(BytesIO(bmp_bytes)).convert("RGB")
                            images.append(image)

                        except Exception as e:
                            print(f"[Scanner] Lỗi khi xử lý trang {page_number + 1}: {e}")

                        if remaining_count == 0:
                            break
                    if time.time() - start_time > 30:
                        # Nếu quá 30 giây mà vẫn chưa nhận được trang, coi như hết trang
                        return (
                            ScanTwainStatus.NO_DOCUMENT,
                            "Không phát hiện tài liệu trong feeder."
                        )

            # ==================================================
            # KHÔNG CÓ TRANG
            # ==================================================

            if not images:
                return (ScanTwainStatus.NO_DOCUMENT, "Không có trang nào được quét.")

            # ==================================================
            # TẠO PDF
            # ==================================================
            images[0].save(
                output_file,
                format="PDF",
                resolution=300.0,
                save_all=True,
                append_images=images[1:]
            )

            # ==================================================
            # GIẢI PHÓNG
            # ==================================================

            for image in images:
                image.close()

    except Exception as e:
        log_exception(e, "SCANNER")
        print(f"[Scanner] Lỗi khi quét: {e}")
        return (ScanTwainStatus.UNKNOWN_ERROR, f"Lỗi khi quét: {e}")
        
    finally:
        if root is not None:
            try:
                root.destroy()
            except Exception:
                pass
    