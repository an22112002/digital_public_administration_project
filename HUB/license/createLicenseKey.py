import base64
import hashlib
import json
import os
import datetime
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


def _get_key(machine_id: str) -> bytes:
    """
    Chuyển machineID thành AES-256 key.
    """
    return hashlib.sha256(
        machine_id.encode("utf-8")
    ).digest()


def create_license(
    expire_date: str,
    machine_id: str,
    output_file: str = "license.key"
):
    """
    Tạo license.key được mã hóa bằng machine_id.
    """

    date = datetime.datetime.strptime(expire_date, "%Y-%m-%d").date()
    if not date:
        print("Ngày hết hạn không hợp lệ.")
        return

    license_data = {
        "machine_id": machine_id,
        "expire_date": expire_date
    }

    plaintext = json.dumps(
        license_data,
        ensure_ascii=False,
        separators=(",", ":")
    ).encode("utf-8")

    key = _get_key(machine_id)

    # AES-GCM cần nonce mới cho mỗi lần mã hóa
    nonce = os.urandom(12)

    aes = AESGCM(key)

    encrypted = aes.encrypt(
        nonce,
        plaintext,
        None
    )

    # nonce + ciphertext + authentication tag
    result = base64.urlsafe_b64encode(
        nonce + encrypted
    ).decode("ascii")

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(result)

if __name__ == "__main__":
    expire_date = input("Nhập ngày hết hạn (YYYY-MM-DD): ").strip()
    machine_id = input("Nhập machine ID: ").strip()
    create_license(expire_date, machine_id)
