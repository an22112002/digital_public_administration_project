import unicodedata
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