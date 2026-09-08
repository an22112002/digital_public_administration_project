import datetime

def format_date(date_str: str, format_str: str = "%d%m%Y") -> str:
    """
    Hàm chuyển đổi định dạng ngày tháng từ ddmmyyyy sang yyyy-mm-dd.
    :param date_str: Chuỗi ngày tháng theo định dạng ddmmyyyy.
    :return: Chuỗi ngày tháng theo định dạng yyyy-mm-dd.
    """
    try:
        # Chuyển đổi chuỗi thành đối tượng datetime
        date_obj = datetime.datetime.strptime(date_str, "%d%m%Y")
        # Chuyển đổi đối tượng datetime thành chuỗi theo định dạng yyyy-mm-dd
        return date_obj.strftime(format_str)
    except ValueError:
        raise ValueError("Định dạng ngày tháng không hợp lệ. Vui lòng sử dụng định dạng ddmmyyyy.")

def isAllUppercase(s: str) -> bool:
    """
    Hàm kiểm tra xem chuỗi có phải là chữ hoa hay không.
    :param s: Chuỗi cần kiểm tra.
    :return: True nếu chuỗi là chữ hoa, False nếu không.
    """
    return s.isupper()

def isContainsNumber(s: str) -> bool:
    """
    Hàm kiểm tra xem chuỗi có chứa số hay không.
    :param s: Chuỗi cần kiểm tra.
    :return: True nếu chuỗi chứa số, False nếu không.
    """
    return any(char.isdigit() for char in s)

def isSimilar(s1: str, s2: str, threshold: float = 0.8) -> bool:
    """
    Hàm kiểm tra xem hai chuỗi có giống nhau hay không, đếm số ký tự.
    :param s1: Chuỗi thứ nhất.
    :param s2: Chuỗi thứ hai.
    :param threshold: Ngưỡng tương đồng (0-1).
    :return: True nếu hai chuỗi giống nhau, False nếu không.
    VD: "các bạn" và "coc ban" sẽ được coi là giống nhau nếu threshold = 0.8
    Ở đây, threshold = 0.8 nghĩa là nếu 80% ký tự giống nhau thì coi là giống nhau.
    Ở đây, chỉ so sánh ký tự, không phân biệt chữ hoa chữ thường
    """
    # Tính toán độ tương đồng giữa hai chuỗi
    if not s1 or not s2:
        return False

    # Đếm số ký tự giống nhau
    common_chars = sum(1 for c1, c2 in zip(s1.lower(), s2.lower()) if c1 == c2)
    max_len = max(len(s1), len(s2))

    similarity = common_chars / max_len
    if similarity >= threshold:
        return True
    return False

def isADate(s: str) -> bool:
    """
    Hàm kiểm tra xem chuỗi có phải là ngày tháng hay không.
    :param s: Chuỗi cần kiểm tra.
    :return: True nếu chuỗi là ngày tháng, False nếu không.
    ddmmyyyy, dd/mm/yyyy, dd-mm-yyyy, dd.mm.yyyy
    """
    try:
        datetime.datetime.strptime(s, "%d%m%Y")
        return True
    except ValueError:
        return False

def isContainString(s: str, substr: str) -> bool:
    """
    Hàm kiểm tra xem chuỗi có chứa chuỗi con hay không.
    :param s: Chuỗi cần kiểm tra.
    :param substr: Chuỗi con cần kiểm tra.
    :return: True nếu chuỗi chứa chuỗi con, False nếu không.
    """
    return substr in s

def isContainSimilarString(s: str, substr: str, threshold: float = 0.8) -> bool:
    """
    Hàm kiểm tra xem chuỗi có chứa chuỗi con giống nhau hay không.
    :param s: Chuỗi cần kiểm tra.
    :param substr: Chuỗi con cần kiểm tra.
    :param threshold: Ngưỡng tương đồng (0-1).
    :return: True nếu chuỗi chứa chuỗi con giống nhau, False nếu không.
    """
    for i in range(len(s) - len(substr) + 1):
        if isSimilar(s[i:i+len(substr)], substr, threshold):
            return True
    return False

def isFirstCharacterUppercase(s: str, threshold: float = 0.8) -> bool:
    """
    Hàm kiểm tra xem ký tự đầu tiên của từng từ trong chuỗi có phải là chữ hoa hay không.
    :param s: Chuỗi cần kiểm tra.
    :param threshold: Ngưỡng tương đồng (0-1).
    :return: True nếu ký tự đầu tiên là chữ hoa, False nếu không.
    """
    strs = s.split(" ")
    len_strs = len(strs)
    count = 0
    for str in strs:
        if str and str[0].isupper():
            count += 1
    if count / len_strs >= threshold:
        return True
    return False

def normalize_date(value: str) -> str | None:
    """
    Chuẩn hóa ngày sinh về dạng ddmmyyyy.

    Hỗ trợ:
        22112002
        22/11/2002
        22-11-2002
        22.11.2002
        2211/2002
        2211-2002
        2211.2002
    """

    if not value:
        return None

    value = value.strip()

    # Chỉ giữ chữ số
    digits = "".join(c for c in value if c.isdigit())

    # Ngày sinh phải có đúng 8 chữ số
    if len(digits) != 8:
        return None

    # Kiểm tra ngày thực tế
    try:
        datetime.datetime.strptime(digits, "%d%m%Y")
    except ValueError:
        return None

    return digits