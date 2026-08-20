# mô phỏng các chức năng của NAPS2 để kiểm tra mà không cần máy scan thực sự
import subprocess
from pathlib import Path
from typing import Literal
from enum import Enum

from pypdf import PdfReader


class ScanStatus(Enum):
    SUCCESS = "success"
    NO_DOCUMENT = "no_document"
    PAPER_JAM = "paper_jam"
    DEVICE_BUSY = "device_busy"
    DEVICE_OFFLINE = "device_offline"
    COMMUNICATION_ERROR = "communication_error"
    INVALID_DEVICE = "invalid_device"
    UNKNOWN_ERROR = "unknown_error"

# Kiểm tra xem đã cài NAPS2 chưa
# path_to_naps2: đường dẫn đến tệp thực thi NAPS2
# VD: C:\Program Files\NAPS2\NAPS2.Console.exe

def check_naps2_installed(path_to_naps2: str) -> tuple[bool, str]:
    try:
        result = subprocess.run([path_to_naps2, '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode == 0:
            message = result.stderr.decode().strip().split('+')[0]  # Lấy version từ stderr, bỏ phần sau dấu +
            return True, message
        else:
            return False, result.stderr.decode().strip()
    except FileNotFoundError:
        return False, "NAPS2 not found"

# Lấy danh sách các thiết bị scanner được cài đặt trên hệ thống
async def get_list_scanner_devices(path_to_naps2: str, type_driver: Literal["wia", "twain", "escl"]) -> list:
    if type_driver == "wia":
        return ["Mock Scanner 1"]
    elif type_driver == "twain":
        return ["Mock Scanner 2"]
    elif type_driver == "escl":
        return ["Mock Scanner 1", "Mock Scanner 2"]
    else:
        return ["Mock Scanner 1", "Mock Scanner 2"]

async def scan_documents_to_folder(timestamp: int, path_to_naps2: str, output_folder: str, device_name: str, driver: Literal["wia", "twain", "escl"], color_mode: Literal["color", "grayscale", "blackwhite"] = "color") -> tuple[ScanStatus, str | None]:
    output_folder_path = Path(output_folder+f"/patch_{timestamp}")
    output_folder_path.mkdir(parents=True, exist_ok=True)
    # Giả lập việc scan thành công, lấy file PDF từ store và lưu vào output_folder
    store = r"C:\Users\ADMIN\Pictures\store"
    output_pdf_path = output_folder_path / f"scan.pdf"
    # tìm file PDF trong store
    pdf_files = list(Path(store).glob("*.pdf"))
    if not pdf_files:
        return ScanStatus.NO_DOCUMENT, None
    # copy file PDF đầu tiên từ store sang output_folder
    first_pdf = pdf_files[0]
    with open(first_pdf, "rb") as src_file:
        with open(output_pdf_path, "wb") as dst_file:
            dst_file.write(src_file.read())
    return ScanStatus.SUCCESS, None


# OCR các tệp hình ảnh sang PDF
def OCR_images_to_pdf(path_to_naps2: str, input_file: str, output_file: str, language: str = "vie") -> bool:
    try:
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)

        cmd = [
            path_to_naps2,

            # Input image
            "-i", input_file,

            # Không scan, chỉ import image -> PDF
            "-n", "0",

            # Output PDF
            "-o", output_file,

            # Vietnamese + English
            "--ocrlang", "vie+eng",

            # Ghi đè nếu đã tồn tại
            "-f",

            # Hiển thị log
            "-v",
        ]

        print("Running:")
        print(" ".join(f'"{x}"' if " " in x else x for x in cmd))

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace"
        )

        print("STDOUT:")
        print(result.stdout)

        print("STDERR:")
        print(result.stderr)

        if result.returncode != 0:
            raise RuntimeError(
                f"NAPS2 OCR failed. Exit code: {result.returncode}"
            )

        if not Path(output_file).exists():
            raise FileNotFoundError(
                f"Không tìm thấy file OCR: {output_file}"
            )

        return output_file
    except FileNotFoundError:
        return False

if __name__ == "__main__":
    pass