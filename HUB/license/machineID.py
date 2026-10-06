import hashlib
import subprocess


def _powershell(command: str) -> str:
    try:
        result = subprocess.check_output(
            [
                "powershell",
                "-NoProfile",
                "-NonInteractive",
                "-Command",
                command
            ],
            stderr=subprocess.DEVNULL,
            text=True
        )
        return result.strip()
    except Exception:
        return ""


def get_machine_id() -> str:
    bios_serial = _powershell(
        "(Get-CimInstance Win32_BIOS).SerialNumber"
    )

    machine_guid = _powershell(
        "(Get-ItemProperty "
        "'HKLM:\\SOFTWARE\\Microsoft\\Cryptography').MachineGuid"
    )

    raw = f"{bios_serial}|{machine_guid}".strip().lower()

    return hashlib.sha256(raw.encode("utf-8")).hexdigest()

if __name__ == "__main__":
    print(get_machine_id())
    input("Nhấn Enter để thoát...")