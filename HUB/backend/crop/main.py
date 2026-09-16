import cv2
import numpy as np
from ultralytics import YOLO
from pathlib import Path
from PIL import Image
import pymupdf
import time

# vị trí file main
PATH_FOLDER_MODELS = Path(__file__).parent / "models" / "index-card-detector.pt"

# IMAGE_PATH = Path(r"C:\Users\ADMIN\Pictures\page_1.jpg")


# # =========================
# # 1. Đọc ảnh
# # =========================
# image = cv2.imread(str(IMAGE_PATH))

# # =========================
# # 2. Bỏ vùng trắng phía dưới
# # =========================
# mask = np.any(image < 250, axis=2)

# rows = np.where(mask.any(axis=1))[0]

# if len(rows) > 0:
#     last_row = rows[-1]
#     image = image[:last_row + 1, :]

# # =========================
# # 3. YOLO
# # =========================
# model = YOLO(str(PATH_FOLDER_MODELS))

# results = model.predict(
#     image,
#     imgsz=1024,
#     conf=0.25
# )

# result = results[0]

# if result.boxes is None or len(result.boxes) == 0:
#     print("Không tìm thấy card")
#     exit()

# # =========================
# # 4. Lấy card có confidence cao nhất
# # =========================
# best_index = int(result.boxes.conf.argmax())

# box = result.boxes[best_index]

# x1, y1, x2, y2 = (
#     box.xyxy[0]
#     .cpu()
#     .numpy()
#     .astype(int)
# )

# confidence = float(box.conf[0])

# print("Confidence:", confidence)
# print("Box:", x1, y1, x2, y2)

# # =========================
# # 5. Crop từ ảnh gốc đã trim
# # =========================
# card = image[y1:y2, x1:x2]

# crop_rgb = cv2.cvtColor(card, cv2.COLOR_BGR2RGB)

# pil_image = Image.fromarray(crop_rgb)

# pil_image.save(
#     "p1.jpg",
#     dpi=(300, 300),
#     quality=95
# )

def auto_crop_bottom_white(image, enabled=True, min_white_ratio=0.05, white_threshold=250, min_actual_white_ratio=0.99):
    """
    Tự động bỏ vùng trắng phía dưới ảnh.

    enabled=False:
        Giữ nguyên ảnh, không crop.

    Chỉ crop khi:
        - vùng trắng phía dưới >= 5% chiều cao
        - ít nhất 99% pixel trong vùng đó là trắng
    """

    if not enabled:
        return image, False

    h, w = image.shape[:2]

    # Tìm pixel không trắng
    non_white = np.any(
        image < white_threshold,
        axis=2
    )

    rows = np.where(
        non_white.any(axis=1)
    )[0]

    if len(rows) == 0:
        return image, False

    # Dòng cuối cùng có nội dung
    last_content_row = rows[-1]

    # Chiều cao vùng trắng phía dưới
    white_height = h - 1 - last_content_row

    white_ratio = white_height / h

    # Không đủ lớn -> giữ nguyên
    if white_ratio < min_white_ratio:
        return image, False

    # Lấy riêng vùng trắng phía dưới
    bottom_area = image[
        last_content_row + 1:
    ]

    if bottom_area.size == 0:
        return image, False

    # Kiểm tra vùng đó có thực sự trắng không
    white_pixels = np.all(
        bottom_area >= white_threshold,
        axis=2
    )

    actual_white_ratio = white_pixels.mean()

    # Không đủ trắng -> giữ nguyên
    if actual_white_ratio < min_actual_white_ratio:
        return image, False

    # Chắc chắn là vùng trắng -> crop
    cropped = image[
        :last_content_row + 1,
        :
    ]

    return cropped, True

async def detect_and_crop_image(image_path: str, confidence_min=0.7):
    """
    Dò tìm card trong ảnh và crop ra.

    image_path:
        Đường dẫn đến ảnh đầu vào.
    confidence_min:
        Ngưỡng độ tin cậy cho việc phát hiện document nhỏ.
    """
    # image_path có dạng ".../page_4.jpg"
    # các file crop ra sẽ có dạng ".../page_4_1.jpg", ".../page_4_2.jpg", ...
    output_folder = Path(image_path).parent

    # ==========================================
    # 1. Đọc ảnh
    # ==========================================
    image = cv2.imread(image_path)

    # ==========================================
    # 2. YOLO
    # ==========================================
    model = YOLO(
        str(PATH_FOLDER_MODELS)
    )

    results = model.predict(
        image,
        imgsz=1024,
        conf=confidence_min,
        verbose=False
    )

    # Lưu tất cả các box được phát hiện ra
    result = results[0]

    if (
        result.boxes is None
        or len(result.boxes) == 0
    ):
        print(
            f"[YOLO] Không tìm thấy card "
            f"trong ảnh {image_path}"
        )
        return []

    # ==========================================
    # 3. Crop tất cả các box được phát hiện ra
    # ==========================================
    cropped_paths = []

    for i, box in enumerate(result.boxes):
        x1, y1, x2, y2 = (
            box.xyxy[0]
            .cpu()
            .numpy()
            .astype(int)
        )

        confidence = float(
            box.conf[0]
        )

        print(
            f"[YOLO] {image_path} "
            f"box={i + 1}/{len(result.boxes)} "
            f"confidence={confidence:.4f}"
        )

        # ==========================================
        # Crop card
        # ==========================================
        card = image[
            y1:y2,
            x1:x2
        ]

        crop_rgb = cv2.cvtColor(
            card,
            cv2.COLOR_BGR2RGB
        )

        pil_image = Image.fromarray(
            crop_rgb
        )

        crop_path = (
            output_folder
            / f"{Path(image_path).stem}_{i + 1}.jpg"
        )

        pil_image.save(
            crop_path,
            dpi=(300, 300),
            quality=95
        )

        cropped_paths.append(str(crop_path))

    return cropped_paths

async def crop_with_position(image_path: str, position: list[int]):
    """
    Crop ảnh theo tọa độ đã biết.

    image_path:
        Đường dẫn đến ảnh đầu vào.
    position:
        Tọa độ crop [x1, y1, x2, y2]
    """
    x1, y1, x2, y2 = position

    # image_path có dạng ".../page_4.jpg"
    # file crop ra sẽ có dạng ".../page_4_crop.jpg"
    output_folder = Path(image_path).parent
    crop_path = (
        output_folder
        / f"{Path(image_path).stem}_crop_{int(time.time())}.jpg"
    )

    # ==========================================
    # 1. Đọc ảnh
    # ==========================================
    image = cv2.imread(image_path)

    # ==========================================
    # 2. Crop card
    # ==========================================
    card = image[
        y1:y2,
        x1:x2
    ]

    crop_rgb = cv2.cvtColor(
        card,
        cv2.COLOR_BGR2RGB
    )

    pil_image = Image.fromarray(
        crop_rgb
    )

    pil_image.save(
        crop_path,
        dpi=(300, 300),
        quality=95
    )

    return str(crop_path)

async def extendImage(ex_x, ex_y, image_path: str):
    """
    Mở rộng ảnh theo chiều dài và chiều rộng. Phần mở rộng là các pixel trắng (255,255,255). Rồi lưu lại ảnh mới và trả về đường dẫn mới.
    ex_x: % mở rộng theo chiều dài (x). 0.12 = 12% mở rộng theo chiều dài
    ex_y: % mở rộng theo chiều rộng (y)
    image_path: Đường dẫn đến ảnh đầu vào.
    """
    # Đọc ảnh
    image = cv2.imread(image_path)

    # Tính toán kích thước mới
    height, width = image.shape[:2]
    new_height = int(height * (1 + ex_y))
    new_width = int(width * (1 + ex_x))

    # Tạo ảnh mới với kích thước mới
    extended_image = np.zeros((new_height, new_width, 3), dtype=np.uint8)
    extended_image[:] = [255, 255, 255]  # Màu trắng

    # Đặt ảnh gốc vào giữa ảnh mới
    y_offset = (new_height - height) // 2
    x_offset = (new_width - width) // 2
    extended_image[y_offset:y_offset + height, x_offset:x_offset + width] = image

    # Lưu ảnh mới
    # file cũ lưu ở ".../test/images/page_1.jpg" thì file mới sẽ lưu ở ".../test/extended/page_1.jpg"
    output_path = Path(image_path).parent.parent / "extended" / Path(image_path).name
    output_path.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(output_path), extended_image)

    return str(output_path)

async def splitPDF(
    pdf_path: str,
    begin_int: int,
    output_folder: str,
):
    """
    Chia PDF thành các ảnh JPG riêng lẻ.

    Chức năng:
    - PDF -> ảnh 300 DPI
    - Tự động bỏ vùng trắng phía dưới
    - KHÔNG chạy YOLO
    - KHÔNG crop card

    begin_int:
        Số thứ tự bắt đầu đặt tên page.

    return:
        Danh sách các ảnh page vừa tạo.
    """

    output_path = Path(output_folder)

    output_path.mkdir(
        parents=True,
        exist_ok=True
    )

    created_images = []

    pdf = pymupdf.open(pdf_path)

    try:
        for i, page in enumerate(pdf):

            page_number = i + begin_int

            # ==========================================
            # PDF -> ảnh 300 DPI
            # ==========================================

            pix = page.get_pixmap(
                dpi=300,
                alpha=False
            )

            image = np.frombuffer(
                pix.samples,
                dtype=np.uint8
            ).reshape(
                pix.height,
                pix.width,
                pix.n
            )

            image = cv2.cvtColor(
                image,
                cv2.COLOR_RGB2BGR
            )

            # ==========================================
            # BỎ VÙNG TRẮNG PHÍA DƯỚI
            # ==========================================

            image, white_cropped = auto_crop_bottom_white(
                image,
                enabled=True
            )

            if white_cropped:
                print(
                    f"[WHITE CROP] Page {page_number}: "
                    f"đã bỏ vùng trắng phía dưới"
                )
            else:
                print(
                    f"[WHITE CROP] Page {page_number}: "
                    f"giữ nguyên ảnh"
                )

            # ==========================================
            # LƯU PAGE
            # ==========================================

            crop_path = (
                output_path
                / f"page_{page_number}.jpg"
            )

            crop_rgb = cv2.cvtColor(
                image,
                cv2.COLOR_BGR2RGB
            )

            pil_image = Image.fromarray(
                crop_rgb
            )

            pil_image.save(
                crop_path,
                dpi=(300, 300),
                quality=95
            )

            created_images.append(
                str(crop_path)
            )

            print(
                f"[SPLIT PDF] "
                f"page={page_number} "
                f"saved={crop_path}"
            )

    finally:
        pdf.close()

    return created_images

if __name__ == "__main__":
    import asyncio

    # pdf_path = r"C:\Users\ADMIN\Downloads\lily.pdf"
    # output_folder = r"C:\Users\ADMIN\Pictures\store"

    # asyncio.run(
    #     splitPDF(pdf_path, 1, output_folder)
    # )

    # image_path = r"C:\Users\ADMIN\Pictures\Screenshot_6.jpg"
    # asyncio.run(
    #     detect_and_crop_image(image_path)
    # )

    image_path = r"D:\scan_files\patch_1788410810\images\page_1.jpg"
    asyncio.run(
        extendImage(0.15, 0.25, image_path)
    )