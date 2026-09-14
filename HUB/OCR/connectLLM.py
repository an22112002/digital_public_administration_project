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
   # r"C:\Users\ADMIN\Pictures\Screenshot_7.jpg",
   r"C:\Users\ADMIN\Pictures\phone\cccd_3.jpg",
   r"C:\Users\ADMIN\Pictures\phone\cccd_4.jpg"
   # r"D:\digital_public_administration_project\HUB\cccd.jpg",
   # r"D:\digital_public_administration_project\HUB\cccd_2.jpg"
]

context = """
Bạn là AI chuyên đọc giấy tờ tùy thân từ hình ảnh.

NHIỆM VỤ:
Đọc tất cả ảnh được cung cấp và trả về DUY NHẤT một JSON hợp lệ theo schema
ở cuối.

==================================================
NGUYÊN TẮC CHUNG
==================================================

- CHỈ lấy thông tin nhìn thấy trực tiếp trên ảnh.
- Mỗi field phải xác định theo quan hệ:

    NHÃN TRÊN ẢNH -> GIÁ TRỊ CỦA NHÃN

- Luôn tìm NHÃN trước, sau đó lấy giá trị thuộc đúng nhãn đó.
- Không lấy một giá trị chỉ vì nó nằm ở vị trí có vẻ phù hợp.
- Không dùng field này để suy ra field khác.
- Không đoán, không tính toán, không tự tạo dữ liệu.
- Không tự bổ sung phần thông tin bị thiếu.
- Nếu không xác định chắc chắn -> "UNKNOWN".
- Nếu có nhiều giá trị nhưng không xác định được giá trị nào thuộc nhãn
  cần tìm -> "UNKNOWN".
- Chỉ sửa lỗi OCR khi hình ảnh cho phép xác định rõ.

==================================================
QUY ƯỚC VỊ TRÍ MẶT THẺ
==================================================

Đối với CCCD / thẻ căn cước:

MẶT TRƯỚC:
- Chứa ảnh chân dung

MẶT SAU:
- Không có ảnh chân dung
- Có mã máy đọc.

QUAN TRỌNG:
"Trước / sau" chỉ dùng để XÁC ĐỊNH NƠI TÌM KIẾM.
Không được coi vị trí là bằng chứng thay thế cho nhãn.

==================================================
1. type_document
==================================================

VỊ TRÍ TÌM:
- Cả mặt trước và mặt sau.
- Ưu tiên TIÊU ĐỀ ở phần đầu mặt giấy tờ.

NHÃN / DẤU HIỆU:
- "CĂN CƯỚC CÔNG DÂN"
- "CITIZEN IDENTITY CARD"
- "CĂN CƯỚC"
- "IDENTITY CARD"
- "GIẤY CHỨNG NHẬN CĂN CƯỚC"
- "CHỨNG MINH NHÂN DÂN"
- "PASSPORT"

KẾT QUẢ:
"chứng minh nhân dân"
"thẻ căn cước"
"giấy chứng nhận căn cước"
"hộ chiếu"
"thẻ căn cước công dân"
"UNKNOWN"

==================================================
2. fullname
==================================================

VỊ TRÍ TÌM:
- MẶT TRƯỚC.
- Khu vực thông tin cá nhân, gần ảnh chân dung.

NHÃN:
"HỌ VÀ TÊN"
"FULL NAME"

GIÁ TRỊ:
- Lấy đúng họ tên nằm ngay sau/dưới nhãn.
- Giữ nguyên họ tên nhìn thấy trên ảnh.

KHÔNG LẤY:
- Tên từ MRZ nếu Họ và tên trên mặt trước rõ ràng.

==================================================
3. dob
==================================================

VỊ TRÍ TÌM:
- MẶT TRƯỚC.
- Khu vực thông tin cá nhân.

NHÃN:
"NGÀY SINH"
"DATE OF BIRTH"

GIÁ TRỊ:
- Lấy ngày thuộc đúng nhãn này.
- Định dạng dd/mm/yyyy.

KHÔNG LẤY:
- Ngày cấp.
- Ngày hết hạn.
- Ngày khác trên giấy tờ.

==================================================
4. sex
==================================================

VỊ TRÍ TÌM:
- MẶT TRƯỚC.
- Khu vực thông tin cá nhân.

NHÃN:
"GIỚI TÍNH"
"SEX"

GIÁ TRỊ:
- "Nam" / "Male" / "M" -> "Nam"
- "Nữ" / "Female" / "F" -> "Nữ"

Không suy luận giới tính từ tên.

==================================================
5. id_number
==================================================

VỊ TRÍ TÌM:
- ƯU TIÊN MẶT TRƯỚC.
- Tìm số CCCD/số định danh ở khu vực thông tin chính.
- Có thể kiểm tra MRZ ở MẶT SAU nếu mặt trước không rõ.

NHÃN:
"SỐ CCCD"
"SỐ ĐỊNH DANH CÁ NHÂN"
"IDENTITY CARD NUMBER"
hoặc số 12 chữ số được trình bày ở vị trí số định danh.

GIÁ TRỊ:
- Lấy đúng dãy số thuộc giấy tờ.
- Thông thường là 12 chữ số đối với CCCD/thẻ căn cước.

KHÔNG LẤY:
- Số điện thoại.
- Số hồ sơ.
- Ngày tháng.
- Dãy số khác.

==================================================
6. expiry_date
==================================================

VỊ TRÍ TÌM:
- Ưu tiên MẶT TRƯỚC nhưng cũng có thể có ở MẶT SAU.

NHÃN:
"NGÀY HẾT HẠN"
"DATE OF EXPIRY"
"EXPIRY DATE"
hoặc nhãn tương đương chỉ rõ thời hạn của giấy tờ.

GIÁ TRỊ:
- Chỉ lấy ngày thuộc đúng nhãn ngày hết hạn.
- Định dạng dd/mm/yyyy.

QUAN TRỌNG:
Không lấy ngày chỉ vì nó nằm ở mặt sau.
Phải xác định được quan hệ:
"NGÀY HẾT HẠN" -> ngày tương ứng.

==================================================
7. issue_date
==================================================

VỊ TRÍ TÌM:
- MẶT SAU
- Tìm khu vực có thông tin ngày cấp.

NHÃN:
"NGÀY CẤP"
"DATE OF ISSUE"
"Ngày, tháng, năm/ Date, month year"
hoặc nhãn tương đương nếu ngữ cảnh trên ảnh xác nhận đó là ngày cấp.

GIÁ TRỊ:
- Lấy CHÍNH XÁC ngày thuộc nhãn/ngữ cảnh ngày cấp.
- Định dạng dd/mm/yyyy.

QUY TẮC RẤT QUAN TRỌNG:

Không được coi mọi ngày ở MẶT SAU là issue_date.

Phải xác định theo:
    NHÃN "NGÀY CẤP" -> GIÁ TRỊ NGÀY CẤP

Không được xác định theo:
    MẶT SAU -> một ngày bất kỳ

Không được lấy:
- "Ngày sinh" làm issue_date.
- "Ngày hết hạn" làm issue_date.
- Ngày khác chỉ vì có dạng dd/mm/yyyy.
- Ngày được tính toán hoặc suy ra.
- Ngày không nhìn thấy trực tiếp trên ảnh.

Nếu không xác định được rõ nhãn/ngữ cảnh ngày cấp:
-> "UNKNOWN"

==================================================
8. issue_place
==================================================

VỊ TRÍ TÌM:
- MẶT SAU

NHÃN:
"NƠI CẤP"
"ISSUING AUTHORITY"
"AUTHORITY"
hoặc tên cơ quan xuất hiện trực tiếp trên ảnh.

GIÁ TRỊ CHỈ ĐƯỢC:
"Cục Cảnh sát quản lý hành chính về trật tự xã hội"
"Cục Cảnh sát đăng ký quản lý cư trú và dữ liệu quốc gia về dân cư"
"Bộ Công an"
"Cục Quản lý xuất nhập cảnh"

Trường này phải suy ra từ lần lượt các bước dưới đây:

Bước 1: Nếu type_document là "hộ chiếu" thì chắc chắn issue_place = "Cục Quản lý xuất nhập cảnh".

Bước 2: Nếu có cụm từ "Cục Cảnh sát quản lý hành chính về trật tự xã hội" hoặc "Cục trưởng Cục Cảnh sát quản lý hành chính về trật tự xã hội" thì issue_place = "Cục Cảnh sát quản lý hành chính về trật tự xã hội".

Bước 3: Nếu có cụm từ "Bộ công an" hoặc "BỘ CÔNG AN" thì issue_place = "Bộ Công an".

Bước 4: Nếu qua 3 bước trên vẫn chưa xác định được issue_place thì issue_place = "Cục Cảnh sát đăng ký quản lý cư trú và dữ liệu quốc gia về dân cư".

CHỈ chuẩn hóa về một trong các giá trị trên khi tên cơ quan trên ảnh
tương ứng rõ ràng.

KHÔNG ĐƯỢC:
- Tự mặc định Bộ Công an.
- Tự chọn cơ quan dựa trên loại giấy tờ.
- Thêm từ không xuất hiện trên ảnh.
- Đổi tên cơ quan thành một tên khác.

==================================================
9. hometown
==================================================

VỊ TRÍ TÌM:
- MẶT TRƯỚC.
- Khu vực thông tin cá nhân.

NHÃN:
"QUÊ QUÁN"
"PLACE OF ORIGIN"

GIÁ TRỊ:
- Chỉ lấy địa danh thuộc đúng nhãn này.
- Nếu có nhiều dòng thuộc cùng trường -> ghép bằng dấu phẩy.

KHÔNG LẤY:
- "NƠI THƯỜNG TRÚ".
- "PLACE OF RESIDENCE".
- Địa danh khác chỉ vì nó nằm trên giấy tờ.
- Địa danh tự suy ra.

==================================================
10. address
==================================================

VỊ TRÍ TÌM:
- MẶT TRƯỚC.
- Khu vực thông tin cư trú.

NHÃN:
"NƠI THƯỜNG TRÚ"
"PLACE OF RESIDENCE"

GIÁ TRỊ:
- Chỉ lấy địa chỉ thuộc đúng nhãn này.
- Nếu có nhiều dòng thuộc cùng trường -> ghép bằng dấu phẩy.

KHÔNG LẤY:
- "QUÊ QUÁN".
- "PLACE OF ORIGIN".
- Địa chỉ từ MRZ.
- Địa chỉ chỉ vì nằm ở cuối ảnh.
- Địa danh tự bổ sung.

==================================================
11. NGÀY THÁNG
==================================================

Tất cả ngày được trả về phải có dạng:

dd/mm/yyyy

Ví dụ OCR rõ ràng:
"22111/2002" -> "22/11/2002"

Chỉ sửa khi hình ảnh xác nhận được giá trị đúng.
Không suy đoán.

==================================================
12. KIỂM TRA CUỐI
==================================================

Trước khi trả JSON, kiểm tra từng field:

FIELD -> NHÃN -> VỊ TRÍ -> GIÁ TRỊ

Đặc biệt:

dob:
"NGÀY SINH" -> ngày sinh

expiry_date:
"NGÀY HẾT HẠN" -> ngày hết hạn

issue_date:
"NGÀY CẤP" -> ngày cấp

issue_place:
"NƠI CẤP" -> cơ quan cấp

hometown:
"QUÊ QUÁN" -> quê quán

address:
"NƠI THƯỜNG TRÚ" -> địa chỉ thường trú

Nếu không xác định được quan hệ NHÃN -> GIÁ TRỊ:
-> "UNKNOWN"

==================================================
OUTPUT
==================================================

Chỉ trả về DUY NHẤT JSON hợp lệ.
Không Markdown.
Không giải thích.
Không thêm text.
Không thêm field ngoài schema.

{
    "type_document": "UNKNOWN",
    "fullname": "UNKNOWN",
    "dob": "UNKNOWN",
    "sex": "UNKNOWN",
    "id_number": "UNKNOWN",
    "expiry_date": "UNKNOWN",
    "issue_date": "UNKNOWN",
    "issue_place": "UNKNOWN",
    "hometown": "UNKNOWN",
    "address": "UNKNOWN"
}
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