import unicodedata
# chuyển tiếng việt có dấu sang không dấu

def remove_accents(input_str):
    """
    Hàm loại bỏ dấu tiếng Việt khỏi chuỗi đầu vào.
    :param input_str: Chuỗi đầu vào có dấu.
    :return: Chuỗi đầu ra không dấu.
    VD: "Tiếng Việt có dấu" -> "Tieng_Viet_co_dau"
    """
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return ''.join([c for c in nfkd_form if not unicodedata.combining(c)]).replace(' ', '_')