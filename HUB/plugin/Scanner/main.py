import subprocess
from pathlib import Path
from typing import Literal
from enum import Enum


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
    try:
        result = result = subprocess.run(
            [
                path_to_naps2,
                "--listdevices",
                "--driver", type_driver
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace"
        )
        # print("NAPS2 returncode:", result.returncode)
        # print("NAPS2 stdout:", result.stdout)
        # print("NAPS2 stderr:", result.stderr)
        if result.returncode == 0:
            devices = result.stdout.strip().split('\n')
            devices = [device for device in devices if device]  # Loại bỏ các dòng trống
            return devices
        else:
            return []
    except FileNotFoundError:
        return []

# Scan toàn bộ giấy tờ sang folder JPEG
async def scan_documents_to_folder(
    timestamp: int,
    path_to_naps2: str,
    output_folder: str,
    device_name: str,
    driver: Literal["wia", "twain", "escl"],
    color_mode: Literal["color", "grayscale", "blackwhite"] = "color",
) -> tuple[ScanStatus, str | None]:

    output_folder_path = Path(output_folder) / f"patch_{timestamp}"
    output_folder_path.mkdir(parents=True, exist_ok=True)

    output_file = output_folder_path / "scan.pdf"  # Tên tệp PDF đầu ra

    try:
        result = subprocess.run(
            [
                path_to_naps2,
                "--noprofile",
                "--driver", driver,
                "--device", device_name,
                "--source", "duplex",
                "--bitdepth", color_mode,
                "--dpi", "300",
                "-o", str(output_file),
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=120,
        )

    except FileNotFoundError:
        return ScanStatus.UNKNOWN_ERROR, f"NAPS2 not found: {path_to_naps2}"

    except subprocess.TimeoutExpired:
        return ScanStatus.UNKNOWN_ERROR, "NAPS2 scan timeout"

    except PermissionError:
        return ScanStatus.UNKNOWN_ERROR, "Permission denied"

    except OSError as e:
        return ScanStatus.UNKNOWN_ERROR, str(e)

    stdout = result.stdout or ""
    stderr = result.stderr or ""

    raw_output = f"{stdout}\n{stderr}".strip()

    if result.returncode == 0:
        # check tệp PDF đã được tạo ra chưa
        files = list(output_folder_path.glob("*.pdf"))
        # ko có tệp PDF nào được tạo ra, có thể là do không có giấy tờ được quét
        if not files:
            return ScanStatus.NO_DOCUMENT, "No scanned pages"

        return ScanStatus.SUCCESS, None

    return parse_naps2_error(raw_output)

def parse_naps2_error(
    output: str,
) -> tuple[ScanStatus, str]:

    text = output.lower()

    if "busy" in text:
        return ScanStatus.DEVICE_BUSY, output

    if "offline" in text:
        return ScanStatus.DEVICE_OFFLINE, output

    if "jam" in text:
        return ScanStatus.PAPER_JAM, output

    if (
        "no document" in text
        or "document feeder is empty" in text
        or "feeder is empty" in text
        or "no paper" in text
    ):
        return ScanStatus.NO_DOCUMENT, output

    if (
        "communication" in text
        or "connection" in text
        or "disconnected" in text
    ):
        return ScanStatus.COMMUNICATION_ERROR, output

    if (
        "device" in text
        and (
            "not found" in text
            or "invalid" in text
        )
    ):
        return ScanStatus.INVALID_DEVICE, output

    return ScanStatus.UNKNOWN_ERROR, output


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


# hỗ trợ
def read_pdf_text(pdf_path):
    reader = PdfReader(pdf_path)

    texts = []

    for page in reader.pages:
        text = page.extract_text()
        if text:
            texts.append(text)

    return "\n".join(texts)

if __name__ == "__main__":
    from pypdf import PdfReader
    path_to_naps2 = r"D:\NAPS2\NAPS2.Console.exe"
    if check_naps2_installed(path_to_naps2):
        print("NAPS2 is installed.")
        devices = get_list_scanner_devices(path_to_naps2, "wia")
        print("Scanner devices:", devices)
        success = OCR_images_to_pdf(path_to_naps2, r"C:\Users\ADMIN\Pictures\phone\cccd_1.jpg", "output.pdf", "vie")
        if success:
            print("OCR completed successfully.")
        else:
            print("OCR failed.")

        read_text = read_pdf_text("output.pdf")
        print(read_text)
    else:
        print("NAPS2 is not installed.")