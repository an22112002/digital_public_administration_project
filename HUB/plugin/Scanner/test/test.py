from io import BytesIO
from pathlib import Path
from datetime import datetime

import tkinter as tk
import twain
from PIL import Image


def scan(output_folder: str) -> str | None:
    """
    Scan tài liệu bằng TWAIN.

    - Hiển thị danh sách scanner trên console
    - Người dùng chọn scanner
    - 300 DPI
    - Color
    - Auto scale nếu driver hỗ trợ
    - Tất cả trang -> 1 PDF
    """

    output_dir = Path(output_folder)
    output_dir.mkdir(parents=True, exist_ok=True)

    root = None
    images = []

    try:
        # ==================================================
        # Tkinter làm parent cho TWAIN
        # ==================================================

        root = tk.Tk()
        root.withdraw()

        # ==================================================
        # TWAIN Source Manager
        # ==================================================

        with twain.SourceManager(root) as sm:

            # ==================================================
            # LẤY DANH SÁCH SCANNER
            # ==================================================

            sources = sm.source_list

            if not sources:
                print("Không tìm thấy máy scan TWAIN.")
                return None

            print()
            print("=" * 60)
            print("DANH SÁCH MÁY SCAN")
            print("=" * 60)

            for i, name in enumerate(sources):
                print(f"[{i}] {name}")

            print("=" * 60)

            # ==================================================
            # CHỌN SCANNER
            # ==================================================

            while True:
                try:
                    index = int(input("Chọn máy scan: "))

                    if 0 <= index < len(sources):
                        break

                    print("Số thứ tự không hợp lệ.")

                except ValueError:
                    print("Vui lòng nhập số.")

            scanner_name = sources[index]

            print()
            print(f"Đã chọn: {scanner_name}")

            # ==================================================
            # MỞ SCANNER
            # ==================================================

            source = sm.open_source(scanner_name)

            if source is None:
                print("Không thể mở máy scan.")
                return None

            print("Đã kết nối máy scan.")

            # ==================================================
            # DPI 300
            # ==================================================

            try:
                source.set_capability(
                    twain.ICAP_XRESOLUTION,
                    twain.TWTY_FIX32,
                    300
                )

                print("X DPI: 300")

            except Exception as e:
                print(f"Không đặt được X DPI: {e}")

            try:
                source.set_capability(
                    twain.ICAP_YRESOLUTION,
                    twain.TWTY_FIX32,
                    300
                )

                print("Y DPI: 300")

            except Exception as e:
                print(f"Không đặt được Y DPI: {e}")

            # ==================================================
            # COLOR
            # ==================================================

            try:
                source.set_capability(
                    twain.ICAP_PIXELTYPE,
                    twain.TWTY_UINT16,
                    twain.TWPT_RGB
                )

                print("Color: RGB")

            except Exception as e:
                print(f"Không đặt được Color: {e}")

            # ==================================================
            # AUTO SCALE
            # ==================================================

            try:
                source.set_capability(
                    twain.ICAP_AUTOSIZE,
                    twain.TWTY_UINT16,
                    twain.TWAS_NONE
                )

                print("Auto scale: OK")

            except Exception:
                print("Auto scale: không hỗ trợ -> bỏ qua")

            # ==================================================
            # BẮT ĐẦU SCAN
            # ==================================================

            print()
            print("Đang scan...")
            print("Đặt tài liệu vào scanner.")

            source.request_acquire(
                show_ui=False,
                modal_ui=False
            )

            # ==================================================
            # NHẬN TỪNG TRANG
            # ==================================================

            page_number = 0

            while True:

                result = source.xfer_image_natively()

                if not result:
                    break

                handle, remaining_count = result

                if handle is None:
                    break

                bmp_bytes = twain.dib_to_bm_file(handle)

                if not bmp_bytes:
                    break

                try:
                    image = Image.open(
                        BytesIO(bmp_bytes)
                    ).convert("RGB")

                    images.append(image.copy())

                    page_number += 1

                    print(f"Đã scan trang {page_number}")

                    image.close()

                except Exception as e:
                    print(
                        f"Lỗi xử lý trang {page_number + 1}: {e}"
                    )

                if remaining_count == 0:
                    break

            # ==================================================
            # KHÔNG CÓ TRANG
            # ==================================================

            if not images:
                print()
                print("Không có trang nào được scan.")
                return None

            # ==================================================
            # TẠO PDF
            # ==================================================

            filename = (
                datetime.now().strftime(
                    "%Y%m%d_%H%M%S_%f"
                )
                + ".pdf"
            )

            pdf_path = output_dir / filename

            images[0].save(
                pdf_path,
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

            print()
            print("=" * 60)
            print("SCAN THÀNH CÔNG")
            print("=" * 60)
            print(f"Số trang: {len(images)}")
            print(f"PDF: {pdf_path}")
            print("=" * 60)

            return str(pdf_path)

    except Exception as e:

        print()
        print("=" * 60)
        print("SCAN LỖI")
        print("=" * 60)
        print(repr(e))
        print("=" * 60)

        return None

    finally:

        if root is not None:
            try:
                root.destroy()
            except Exception:
                pass


if __name__ == "__main__":

    output_folder = r"C:\test_scan"

    pdf_path = scan(output_folder)

    if pdf_path:
        print()
        print("Hoàn tất.")
    else:
        print()
        print("Scan thất bại hoặc người dùng hủy.")

    input("\nNhấn Enter để thoát...")