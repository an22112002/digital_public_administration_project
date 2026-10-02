# chứng nhận kết hôn
from backend.services.LLMServices import runPromptInLMStudio
from backend.utils import image_to_base64
import json
import re
import datetime
import re
import requests
import unicodedata
import re
from functools import lru_cache


BASE_URL = "https://provinces.open-api.vn/api/v2"

async def CNKH_LLM(images: list[str], server_ip: str) -> dict:
    """
    Xử lý OCR cho giấy tờ chứng nhận kết hôn.
    Gửi prompt và hình ảnh đến LM Studio server để xử lý OCR CCCD.
    """
    prompts = [
    """
    Đây là giấy tờ chứng nhận kết hôn hoặc giấy tờ liên quan đến hôn nhân, vui lòng xác định vị trí ủy ban nhân dân cấp giấy: xã/phường, quận/huyện, tỉnh/thành phố; số đăng ký; quyển số đăng ký; ngày đăng ký. Trả lời bằng json duy nhất
    {"commune": .., "district": .., "province": .., "number": .., "serial_number": .., "registration_date": ..}
    - commune là xã/phường
    - district là quận/huyện, lưu ý quận/huyện có thể có hoặc không
    - province là tỉnh/thành phố
    - number là số đăng ký
    - serial_number là quyển số đăng ký
    - registration_date là ngày đăng ký. 
    Các trường không có dữ liệu thì trả về "UNKNOWN". Nếu không xác định được trường nào thì trả về "UNKNOWN" cho trường đó.
    """,
    ]

    img_base64_list = [image_to_base64(image) for image in images]

    json_results = {}

    for prompt in prompts:
        response = await runPromptInLMStudio(
            prompt=prompt,
            images_base64=img_base64_list,
            server_ip=server_ip
        )

        if not response:
            raise ValueError("LM Studio trả về response rỗng")

        try:
            json_return = parse_json_response(response)
            print(json_return)
            for key, value in json_return.items():
                json_results[key] = value
        except json.JSONDecodeError as e:
            print("[CNKH_LLM] Không parse được JSON:")
            # print(repr(response))
            raise ValueError(
                f"LM Studio trả về dữ liệu không phải JSON: {response!r}"
            ) from e

    print(json_results)

    try:
        json_results["commune"] = json_results.get("commune", "UNKNOWN").upper()
        json_results["district"] = json_results.get("district", "UNKNOWN").upper()
        json_results["province"] = json_results.get("province", "UNKNOWN").upper()
        address = resolve_address(
            commune=json_results.get("commune", ""),
            district=json_results.get("district", ""),
            province=json_results.get("province", "")
        )
        if address["commune"]:
            json_results["commune"] = address["commune"].upper()
        if address["province"]:
            json_results["province"] = address["province"].upper()

        json_results["number"] = json_results.get("number", "UNKNOWN").upper()
        json_results["serial_number"] = json_results.get("serial_number", "UNKNOWN").upper()
        json_results["registration_date"] = format_date(json_results.get("registration_date", "UNKNOWN"))

        return json_results
    except json.JSONDecodeError as e:
        print("[CNKH_LLM] Không parse được JSON:")
        # print(repr(response))
        raise ValueError(
            f"LM Studio trả về dữ liệu không phải JSON: {response!r}"
        ) from e

def parse_json_response(response: str) -> dict:
    response = response.strip()

    # Bỏ ```json ... ``` hoặc ``` ... ```
    if response.startswith("```"):
        response = re.sub(r"^```(?:json)?\s*", "", response, flags=re.IGNORECASE)
        response = re.sub(r"\s*```$", "", response)

    return json.loads(response)

def format_date(date_str: str) -> str:
    if not date_str:
        return "00000000"

    date_str = date_str.strip()

    if date_str.upper() == "UNKNOWN":
        return "00000000"

    # Chỉ có năm
    if len(date_str) == 4 and date_str.isdigit():
        return "0101" + date_str

    formats = (
        "%d/%m/%Y",
        "%d-%m-%Y",
        "%d.%m.%Y",
        "%Y-%m-%d",
        "%Y/%m/%d",
        "%Y.%m.%d",
    )

    for fmt in formats:
        try:
            date = datetime.datetime.strptime(date_str, fmt)
            return date.strftime("%d%m%Y")
        except ValueError:
            continue

    return "00000000"


def normalize_name(value: str) -> str:
    """
    Chuẩn hóa tên địa danh để so sánh.

    Ví dụ:
        "Phường Hoàng Kiếm" -> "hoang kiem"
        "P. Hoàng Kiếm"     -> "hoang kiem"
        "HOÀNG KIẾM"        -> "hoang kiem"
        "quận Hoàn Kiếm"    -> "hoan kiem"
    """
    if not value or value == "UNKNOWN":
        return ""

    value = value.strip().lower()

    # Chuẩn hóa một số viết tắt thường gặp
    value = re.sub(r"\b(tp\.?|t\.p\.?)\b", "thanh pho", value)
    value = re.sub(r"\bq\.?\b", "quan", value)
    value = re.sub(r"\bh\.?\b", "huyen", value)
    value = re.sub(r"\bp\.?\b", "phuong", value)
    value = re.sub(r"\bx\.?\b", "xa", value)

    # Bỏ tiền tố hành chính
    prefixes = [
        "thành phố trung ương",
        "thành phố",
        "tỉnh",
        "quận",
        "huyện",
        "thị xã",
        "thành phố thuộc tỉnh",
        "phường",
        "xã",
        "thị trấn",
        "đặc khu",
        "quan",
        "huyen",
        "phuong",
        "xa",
        "thi xa",
        "dac khu",
        "thanh pho",
    ]

    # Lặp vì có thể sau khi thay viết tắt lại sinh ra tiền tố
    changed = True

    while changed:
        changed = False

        for prefix in prefixes:
            if value.startswith(prefix + " "):
                value = value[len(prefix):].strip()
                changed = True
                break

    # Bỏ dấu tiếng Việt
    value = unicodedata.normalize("NFD", value)
    value = "".join(
        c for c in value
        if unicodedata.category(c) != "Mn"
    )

    value = value.replace("đ", "d")

    # Chỉ giữ chữ/số/khoảng trắng
    value = re.sub(r"[^a-z0-9\s]", " ", value)

    value = re.sub(r"\s+", " ", value)

    return value.strip()


@lru_cache(maxsize=1)
def load_address_data():
    """
    Load toàn bộ tỉnh + xã/phường hiện tại.

    Chỉ gọi API một lần trong suốt vòng đời process.
    """

    response = requests.get(
        f"{BASE_URL}/",
        params={"depth": 2},
        timeout=15,
    )

    response.raise_for_status()

    provinces = response.json()

    wards = []

    for province in provinces:

        province_code = province["code"]
        province_name = province["name"]

        # API v2 depth=2 trả danh sách wards
        # trong province
        for ward in province.get("wards", []):

            wards.append({
                "code": ward["code"],
                "name": ward["name"],
                "division_type": ward.get("division_type"),
                "province_code": province_code,
                "province_name": province_name,
            })

    return provinces, wards


def resolve_address(
    commune: str = "",
    district: str = "",
    province: str = "",
):
    """
    Xác định xã/phường và tỉnh/thành hiện tại.

    Không yêu cầu phải có đủ 3 tham số.

    Parameters
    ----------
    commune:
        Xã/phường trên giấy tờ.

    district:
        Quận/huyện trên giấy tờ cũ.

    province:
        Tỉnh/thành phố trên giấy tờ.

    Returns
    -------
    dict

    Ví dụ:

    {
        "commune": "Phường Hoàng Kiếm",
        "province": "Thành phố Hà Nội",
        "valid": True
    }

    Nếu không đủ thông tin để xác định:

    {
        "commune": None,
        "province": "Thành phố Hà Nội",
        "valid": False
    }
    """

    commune = (commune or "").strip()
    district = (district or "").strip()
    province = (province or "").strip()

    provinces, wards = load_address_data()

    province_norm = normalize_name(province)
    commune_norm = normalize_name(commune)
    district_norm = normalize_name(district)

    # =========================================================
    # 1. Tìm province
    # =========================================================

    matched_provinces = []

    if province_norm:

        for p in provinces:

            if normalize_name(p["name"]) == province_norm:
                matched_provinces.append(p)

    # Nếu có province nhưng không tìm thấy
    if province and not matched_provinces:
        return {
            "commune": None,
            "province": None,
            "valid": False,
        }

    # Nếu không có province -> tìm trên toàn quốc
    province_candidates = (
        matched_provinces
        if matched_provinces
        else provinces
    )

    province_codes = {
        p["code"]
        for p in province_candidates
    }

    # =========================================================
    # 2. Nếu có commune -> tìm commune trước
    # =========================================================

    if commune_norm:

        candidates = [
            w for w in wards
            if w["province_code"] in province_codes
            and normalize_name(w["name"]) == commune_norm
        ]

        if len(candidates) == 1:

            w = candidates[0]

            return {
                "commune": w["name"],
                "province": w["province_name"],
                "valid": True,
            }

        # Nếu commune trùng nhiều nơi nhưng district
        # có thể giúp xác định -> xử lý tiếp bên dưới

        if len(candidates) > 1 and district_norm:

            # district cũ có thể chính là tên commune hiện tại
            candidates2 = [
                w for w in candidates
                if normalize_name(w["name"]) == district_norm
            ]

            if len(candidates2) == 1:

                w = candidates2[0]

                return {
                    "commune": w["name"],
                    "province": w["province_name"],
                    "valid": True,
                }

    # =========================================================
    # 3. district cũ có thể chính là commune hiện tại
    #
    # Ví dụ:
    #
    # commune  = ""
    # district = "Hoàng Kiếm"
    # province = "Hà Nội"
    #
    # => "Phường Hoàng Kiếm"
    # =========================================================

    if district_norm:

        candidates = [
            w for w in wards
            if w["province_code"] in province_codes
            and normalize_name(w["name"]) == district_norm
        ]

        if len(candidates) == 1:

            w = candidates[0]

            return {
                "commune": w["name"],
                "province": w["province_name"],
                "valid": True,
            }

    # =========================================================
    # 4. Chỉ có province
    # =========================================================

    if len(matched_provinces) == 1:

        return {
            "commune": None,
            "province": matched_provinces[0]["name"],
            "valid": False,
        }

    # =========================================================
    # 5. Không đủ thông tin
    # =========================================================

    return {
        "commune": None,
        "province": None,
        "valid": False,
    }