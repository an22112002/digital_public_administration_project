import unicodedata
import base64
from PIL import Image
from io import BytesIO
# chuyển tiếng việt có dấu sang không dấu

def remove_accents(input_str, length_limit=50):
    """
    Hàm loại bỏ dấu tiếng Việt khỏi chuỗi đầu vào.
    :param input_str: Chuỗi đầu vào có dấu.
    :param length_limit: Giới hạn độ dài của chuỗi đầu ra.
    :return: Chuỗi đầu ra không dấu.
    VD: "Tiếng Việt có dấu/hello" -> "Tieng_Viet_co_dau-hello"
    """
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    result = ''.join([c for c in nfkd_form if not unicodedata.combining(c)]).replace(' ', '_').replace('/', '-')
    return result[:length_limit]

def image_to_base64(image_path: str, max_size: int = 1600) -> str:
    image = Image.open(image_path)

    # Giữ nguyên tỉ lệ, chỉ thu nhỏ nếu ảnh quá lớn
    image.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)

    buffer = BytesIO()
    image.save(
        buffer,
        format="JPEG",
        quality=90,
        optimize=True
    )

    return base64.b64encode(buffer.getvalue()).decode("utf-8")