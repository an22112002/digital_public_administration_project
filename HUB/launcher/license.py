import base64
import json
from datetime import date
from pathlib import Path

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from license.machineID import get_machine_id
from license.createLicenseKey import _get_key


def load_license(
    machine_id: str,
    license_file: Path
):
    try:
        with open(
            license_file,
            "r",
            encoding="utf-8"
        ) as f:
            encrypted_data = f.read().strip()

        if not encrypted_data:
            return None

        encrypted_bytes = base64.urlsafe_b64decode(
            encrypted_data
        )

        if len(encrypted_bytes) <= 12:
            return None

        nonce = encrypted_bytes[:12]
        ciphertext = encrypted_bytes[12:]

        key = _get_key(machine_id)

        aes = AESGCM(key)

        decrypted_bytes = aes.decrypt(
            nonce,
            ciphertext,
            None
        )

        license_data = json.loads(
            decrypted_bytes.decode("utf-8")
        )

        if not isinstance(license_data, dict):
            return None

        return license_data

    except Exception as e:

        print(
            f"[License] Load failed: {e}"
        )

        return None


def check_license(
    license_path: Path
):
    """
    Kiểm tra license hiện tại.

    Return:
        {
            "valid": True/False,
            "reason": ...,
            "expire_date": ...
        }
    """

    # -------------------------------
    # File không tồn tại
    # -------------------------------

    if not license_path.exists():

        return {
            "valid": False,
            "reason": "missing"
        }

    # -------------------------------
    # Machine ID
    # -------------------------------

    machine_id = get_machine_id()

    # -------------------------------
    # Load license
    # -------------------------------

    license_data = load_license(
        machine_id,
        license_path
    )

    if license_data is None:

        return {
            "valid": False,
            "reason": "invalid"
        }

    # -------------------------------
    # Machine ID
    # -------------------------------

    license_machine_id = license_data.get(
        "machine_id"
    )

    if license_machine_id != machine_id:

        return {
            "valid": False,
            "reason": "invalid"
        }

    # -------------------------------
    # Expire date
    # -------------------------------

    expire_date_string = license_data.get(
        "expire_date"
    )

    if not expire_date_string:

        return {
            "valid": False,
            "reason": "invalid"
        }

    try:

        expire_date = date.fromisoformat(
            expire_date_string
        )

    except ValueError:

        return {
            "valid": False,
            "reason": "invalid"
        }

    # -------------------------------
    # Expired
    # -------------------------------

    if date.today() > expire_date:

        return {
            "valid": False,
            "reason": "expired",
            "expire_date": expire_date_string
        }

    # -------------------------------
    # Valid
    # -------------------------------

    return {
        "valid": True,
        "reason": None,
        "expire_date": expire_date_string,
        "data": license_data
    }