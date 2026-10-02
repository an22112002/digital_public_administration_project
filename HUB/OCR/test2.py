from backend.utils import image_to_base64
from backend.services.LLMServices import runPromptInLMStudio
import re, json, datetime

async def CCCD_LLM(images: list[str], server_ip: str) -> dict:
    """
    Gửi prompt và hình ảnh đến LM Studio server để xử lý OCR CCCD.
    """
    prompts = [
    """
    xác định loại giấy tờ, mã giấy tờ và xác định họ tên, ngày sinh, giới tính, quê quán, nơi thường trú của cá nhân chủ thể của giấy tờ. Trả lời bằng json duy nhất
    {"type_document": .., "id_number": .., "fullname": .., "dob": .., "sex": .., "nationally": .., "hometown": .., "address": ..}
    - type_document phải là một trong các giá trị:
    "chứng minh nhân dân"
    "hộ chiếu"
    "căn cước công dân"
    - id_number phải là dãy số 12 chữ số
    - fullname là tên người, cố gắng xác định dõ dấu chữ, được phép tự suy luận fullname
    - hometown là quê quán, nơi khai sinh
    - address là nơi thường trú, nơi cư trú
    """,
    """
    xác định thông tin cấp giấy tờ: ngày hết hạn, ngày cấp, nơi cấp. Trả lời bằng json duy nhất
    {"expiry_date": .., "issue_date": .., "issue_place": ..}
    - expiry_date thường là ngày nhưng cũng có thể là text "Không thời hạn"
    - issue_place có thể không được ghi dõ ràng trên ảnh, nhưng chỉ được chọn một trong các giá trị sau:
    "Cục Cảnh sát quản lý hành chính về trật tự xã hội"
    "Cục Cảnh sát đăng ký quản lý cư trú và dữ liệu quốc gia về dân cư"
    "Bộ Công an"
    "Cục Quản lý xuất nhập cảnh"
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
            print("[CCCD_LLM] Không parse được JSON:")
            # print(repr(response))
            raise ValueError(
                f"LM Studio trả về dữ liệu không phải JSON: {response!r}"
            ) from e

    print(json_results)

    try:
        json_results["fullname"] = json_results.get("fullname", "UNKNOWN").upper()
        json_results["dob"] = format_date(json_results.get("dob", "UNKNOWN"))
        json_results["sex"] = json_results.get("sex", "UNKNOWN")
        json_results["hometown"] = json_results.get("hometown", "UNKNOWN")
        json_results["address"] = json_results.get("address", "UNKNOWN")
        json_results["issue_place"] = json_results.get("issue_place", "UNKNOWN")
        json_results["expiry_date"] = format_date(json_results.get("expiry_date", "UNKNOWN"))
        json_results["issue_date"] = format_date(json_results.get("issue_date", "UNKNOWN"))
        return json_results
    except json.JSONDecodeError as e:
        print("[CCCD_LLM] Không parse được JSON:")
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

# chuyển 01/01/2000 -> 01012000
# input: dd/mm/yyyy | dd-mm-yyyy | dd.mm.yyyy
#        yyyy-mm-dd | yyyy/mm/dd | yyyy.mm.dd
#        yyyy | UNKNOWN
# output: ddmmyyyy | 00000000 if input is UNKNOWN
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


async def main():
    images = [r"C:\Users\ADMIN\Pictures\Screenshot_12.jpg", r"C:\Users\ADMIN\Pictures\Screenshot_11.jpg"]
    final = await CCCD_LLM(images=images, server_ip="localhost")
    print(final)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())