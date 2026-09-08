import requests
import time
import base64

begin = time.time()

# ocr_text = """
# **Mặt trước**
# CÔNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM
# Độc lập Tự do Hạnh phúc
# SOCIALISTREPUBLIC OF VIETNAM
# Independence Freedom Happiness
# CĂN CƯỚC CÔNG DÂN
# Citizen Identity Card
# 037202004823
# Họ và tên/Full name
# NGUYỄN NGÔ AN
# Ngày sinh/Date of birth
# 22111/2002
# Giới tính/Sex Nam
# Quốc tịch INationality Việt Nam
# Quê quán Place oforigin
# Khánh Nhạc, Yên Khánh, Ninh Bình
# Nơi thường trú / Place of residence
# Phúc Nam
# Có gia trị đến 22/11/2027
# Date of expiry
# Phúc Thành, Thành phố Ninh Bình, Ninh Bình
# **Mặt sau**
# Đặc điểm nhân dang Personalidentification
# nốt ruối c. 2cm dưới trước đuôi
# mắt phải
# Ngày tháng, năm/Date, month year13/05/2021
# CỤC TRƯỜNG CUC CẢNH SÁT
# QUẦN LÝ HÀNH CHÍNH VỀ TRẬT TƯ XÃ HỜI
# DIRECTOR GENERAL OF THE POLICE DEPARTMENT
# FOR ADMINISTRATIVE MANAGEMENTOE SOCIAL ORDER
# Ngôn trở trái
# Ngôn trở phải
# UNINTERS
# Letfindexinger
# Eightindextanger
# Phạm Công Nguyên
# IDVNM2020048235037202004823KK1
# 0211222M2711221VNMCKKKKKKKCKCKKKKK4
# NGUYENKKNGOKANCKCCCCKKKKKKKKKKCKKKKKKKKKKKKKKK
# """

images = [
   r"C:\Users\ADMIN\Pictures\Screenshot_7.jpg",
   # r"C:\Users\ADMIN\Pictures\phone\cccd_1.jpg",
   # r"C:\Users\ADMIN\Pictures\phone\cccd_2.jpg"
]

context = prompt = f"""
Bạn là hệ thống trích xuất thông tin từ OCR của Căn cước công dân Việt Nam.

Nhiệm vụ:
Xem ảnh CCCD và trả về DUY NHẤT một JSON hợp lệ.

QUY TẮC:

1. fullname:
   - Lấy từ "Họ và tên / Full name".
   - Viết đúng họ tên tiếng Việt.
   - Không lấy tên từ MRZ nếu phần Họ và tên rõ ràng.

2. dob:
   - Lấy "Ngày sinh / Date of birth".
   - Chuẩn hóa thành dd/mm/yyyy.
   - Có thể sửa lỗi OCR rõ ràng như thiếu hoặc thừa ký tự.
   - Có thể đối chiếu với MRZ nếu cần.
   - Không được tự đoán nếu không đủ căn cứ.

3. sex:
   - Chỉ được trả về "Nam" hoặc "Nữ".
   - Nếu OCR ghi "M" trong MRZ thì là "Nam".
   - Nếu OCR ghi "F" trong MRZ thì là "Nữ".

4. CCCD_id:
   - Lấy số CCCD/CMND.
   - CCCD hiện tại thường có đúng 12 chữ số.
   - Ưu tiên số nằm ngay dưới tiêu đề CĂN CƯỚC CÔNG DÂN.
   - Không lấy số từ MRZ nếu số CCCD ở mặt trước đã rõ.

5. issue_date:
   - KHÔNG PHẢI date of expiry.
   - Thường nằm sau "Ngày tháng, năm / Date, month year".
   - Chuẩn hóa thành dd/mm/yyyy.

6. issue_place:
   - Lấy nơi cấp ở mặt sau.
   - Chỉ được chọn một trong các giá trị sau:
     "Cục Cảnh sát đăng ký quản lý cư trú và dữ liệu quốc gia về dân cư"
     "Cục Cảnh sát quản lý hành chính về trật tự xã hội"
     "Bộ Công an"
     "Cục Quản lý xuất nhập cảnh"
   - Nếu OCR có lỗi nhưng có thể xác định chắc chắn thì sửa lại.
   - Nếu không xác định chắc chắn thì trả về "".

7. address:
   - Chỉ lấy NƠI THƯỜNG TRÚ / PLACE OF RESIDENCE.
   - Không lấy QUÊ QUÁN / PLACE OF ORIGIN.
   - Nếu địa chỉ bị OCR tách thành nhiều dòng thì ghép lại bằng dấu phẩy.
   - Không tự thêm địa danh không xuất hiện trong OCR.
   - Trong địa chỉ thường có các từ TỈNH, THÀNH PHỐ, QUẬN, HUYỆN, PHƯỜNG, XÃ, THỊ TRẤN.
   - Địa chỉ thường nằm dưới cùng của mặt trước CCCD.
   
8. Nếu một trường không xác định được chắc chắn, trả về chuỗi rỗng "".

9. Không giải thích.
10. Không sử dụng Markdown.
11. Không đặt JSON trong ```json.
12. Chỉ trả về JSON hợp lệ theo đúng schema dưới đây.

Schema:
{{
    "fullname": "",
    "dob": "",
    "sex": "",
    "CCCD_id": "",
    "issue_date": "",
    "issue_place": "",
    "address": ""
}}
"""

def image_to_base64(image_path: str) -> str: 
   with open(image_path, "rb") as f: 
      return base64.b64encode(f.read()).decode("utf-8")

images_urls = []

for image in images:
   url = image_to_base64(image)
   images_urls.append(
      {
         "type": "image_url",
         "image_url": {
            "url": "data:image/jpeg;base64," + url
         }
      }
   )

content = {
   "role": "user",
   "content": [{
      "type": "text",
      "text": context
   }]
}

content["content"].extend(images_urls)

response = requests.post(
   "http://127.0.0.1:1234/v1/chat/completions",
   json={
      "model": "local-model",
      "messages": [content],
      "temperature": 0,
      "max_tokens": 512,
   },
   timeout=120,
)

response.raise_for_status()

data = response.json()

print(data["choices"][0]["message"]["content"])
end = time.time()
print(f"Thời gian chạy: {float(end - begin): .2f} giây")