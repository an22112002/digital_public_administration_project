SET NAMES utf8mb4;

CREATE DATABASE IF NOT EXISTS HUB_db
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE HUB_db;

CREATE TABLE `provinces`(
    `provinceID` BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(255) NOT NULL
);
CREATE TABLE `communes`(
    `communeID` BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `provinceID` BIGINT NOT NULL,
    `name` VARCHAR(255) NOT NULL
);
CREATE TABLE `extention_documents`(
    `edID` BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `name` TEXT NOT NULL,
    `description` TEXT NULL,
    `OCRtab` VARCHAR(255) NULL
);
CREATE TABLE `services`(
    `serviceID` BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `title` TEXT NOT NULL COMMENT 'dùng để hiện thị trên giao diện',
    `realTitle` TEXT NOT NULL COMMENT 'tên dịch vụ hiển trên web vneid',
    `url` TEXT NOT NULL COMMENT 'url mở trang web upload tài liệu',
    `buttonPosition` INT NOT NULL DEFAULT 1,
    `processes` JSON NOT NULL,
    `active` BOOLEAN NOT NULL DEFAULT TRUE
);
CREATE TABLE `default_documents`(
    `ddID` BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `serviceID` BIGINT NOT NULL,
    `name` TEXT NOT NULL,
    `realName` TEXT NOT NULL,
    `description` TEXT NULL,
    `required` BOOLEAN NOT NULL,
    `OCRtab` VARCHAR(255) NULL
);
CREATE TABLE `scan_documents`(
    `sdID` BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `serviceID` BIGINT NOT NULL,
    `name` TEXT NOT NULL,
    `description` TEXT NULL,
    `OCRtab` VARCHAR(255) NULL
);
ALTER TABLE
    `communes` ADD CONSTRAINT `communes_provinceid_foreign` FOREIGN KEY(`provinceID`) REFERENCES `provinces`(`provinceID`) ON DELETE CASCADE;;
ALTER TABLE
    `default_documents` ADD CONSTRAINT `default_documents_serviceid_foreign` FOREIGN KEY(`serviceID`) REFERENCES `services`(`serviceID`) ON DELETE CASCADE;

INSERT INTO `provinces` (`provinceID`, `name`) VALUES (1, 'Thành phố Hà Nội');
INSERT INTO `provinces` (`provinceID`, `name`) VALUES (2, 'Thành phố Hồ Chí Minh');

INSERT INTO `communes` (`provinceID`, `name`) VALUES (1, 'Phường Ba Đình');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (1, 'Phường Ngọc Hà');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (1, 'Phường Giảng Võ');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (1, 'Phường Hoàn Kiếm');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (1, 'Phường Cửa Nam');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (1, 'Phường Phú Thượng');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (1, 'Phường Hồng Hà');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (1, 'Phường Tây Hồ');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (1, 'Phường Bồ Đề');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (1, 'Phường Việt Hưng');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (1, 'Phường Phúc Lợi');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (1, 'Phường Long Biên');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (1, 'Phường Nghĩa Đô');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (1, 'Phường Cầu Giấy');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (1, 'Phường Yên Hòa');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (1, 'Phường Ô Chợ Dừa');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (1, 'Phường Láng');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (1, 'Phường Văn Miếu - Quốc Tử Giám');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (1, 'Phường Kim Liên');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (1, 'Phường Đống Đa');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (1, 'Phường Hai Bà Trưng');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (1, 'Phường Vĩnh Tuy');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (1, 'Phường Bạch Mai');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (1, 'Phường Vĩnh Hưng');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (1, 'Phường Định Công');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (1, 'Phường Tương Mai');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (1, 'Phường Lĩnh Nam');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (1, 'Phường Hoàng Mai');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (1, 'Phường Hoàng Liệt');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (1, 'Phường Yên Sở');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (1, 'Phường Phương Liệt');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (1, 'Phường Khương Đình');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (1, 'Phường Thanh Xuân');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (1, 'Xã Sóc Sơn');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (1, 'Xã Kim Anh');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (1, 'Xã Trung Giã');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (1, 'Xã Đa Phúc');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (1, 'Xã Nội Bài');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (1, 'Xã Đông Anh');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (1, 'Xã Phúc Thịnh');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (1, 'Xã Thư Lâm');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (1, 'Xã Thiên Lộc');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (1, 'Xã Vĩnh Thanh');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (1, 'Xã Phù Đổng');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (1, 'Xã Thuận An');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (1, 'Xã Gia Lâm');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (1, 'Xã Bát Tràng');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (1, 'Phường Từ Liêm');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (1, 'Phường Thượng Cát');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (1, 'Phường Đông Ngạc');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (1, 'Phường Xuân Đỉnh');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (1, 'Phường Tây Tựu');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (1, 'Phường Phú Diễn');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (1, 'Phường Xuân Phương');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (1, 'Phường Tây Mỗ');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (1, 'Phường Đại Mỗ');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (1, 'Xã Thanh Trì');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (1, 'Phường Thanh Liệt');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (1, 'Xã Đại Thanh');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (1, 'Xã Ngọc Hồi');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (1, 'Xã Nam Phù');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (1, 'Xã Yên Xuân');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (1, 'Xã Quang Minh');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (1, 'Xã Yên Lãng');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (1, 'Xã Tiến Thắng');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (1, 'Xã Mê Linh');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (1, 'Phường Kiến Hưng');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (1, 'Phường Hà Đông');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (1, 'Phường Yên Nghĩa');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (1, 'Phường Phú Lương');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (1, 'Phường Sơn Tây');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (1, 'Phường Tùng Thiện');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (1, 'Xã Đoài Phương');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (1, 'Xã Quảng Oai');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (1, 'Xã Cổ Đô');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (1, 'Xã Minh Châu');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (1, 'Xã Vật Lại');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (1, 'Xã Bất Bạt');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (1, 'Xã Suối Hai');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (1, 'Xã Ba Vì');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (1, 'Xã Yên Bài');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (1, 'Xã Phúc Thọ');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (1, 'Xã Phúc Lộc');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (1, 'Xã Hát Môn');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (1, 'Xã Đan Phượng');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (1, 'Xã Liên Minh');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (1, 'Xã Ô Diên');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (1, 'Xã Hoài Đức');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (1, 'Xã Dương Hòa');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (1, 'Xã Sơn Đồng');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (1, 'Xã An Khánh');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (1, 'Phường Dương Nội');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (1, 'Xã Quốc Oai');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (1, 'Xã Kiều Phú');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (1, 'Xã Hưng Đạo');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (1, 'Xã Phú Cát');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (1, 'Xã Thạch Thất');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (1, 'Xã Hạ Bằng');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (1, 'Xã Hòa Lạc');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (1, 'Xã Tây Phương');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (1, 'Phường Chương Mỹ');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (1, 'Xã Phú Nghĩa');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (1, 'Xã Xuân Mai');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (1, 'Xã Quảng Bị');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (1, 'Xã Trần Phú');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (1, 'Xã Hòa Phú');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (1, 'Xã Thanh Oai');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (1, 'Xã Bình Minh');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (1, 'Xã Tam Hưng');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (1, 'Xã Dân Hòa');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (1, 'Xã Thường Tín');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (1, 'Xã Hồng Vân');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (1, 'Xã Thượng Phúc');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (1, 'Xã Chương Dương');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (1, 'Xã Phú Xuyên');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (1, 'Xã Phượng Dực');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (1, 'Xã Chuyên Mỹ');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (1, 'Xã Đại Xuyên');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (1, 'Xã Vân Đình');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (1, 'Xã Ứng Thiên');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (1, 'Xã Ứng Hòa');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (1, 'Xã Hòa Xá');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (1, 'Xã Mỹ Đức');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (1, 'Xã Phúc Sơn');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (1, 'Xã Hồng Sơn');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (1, 'Xã Hương Sơn');

INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Phường Thủ Dầu Một');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Phường Phú Lợi');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Phường Bình Dương');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Phường Phú An');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Phường Chánh Hiệp');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Xã Dầu Tiếng');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Xã Minh Thạnh');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Xã Long Hòa');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Xã Thanh An');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Phường Bến Cát');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Xã Trừ Văn Thố');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Xã Bàu Bàng');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Phường Chánh Phú Hòa');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Phường Long Nguyên');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Phường Tây Nam');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Phường Thới Hòa');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Phường Hòa Lợi');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Xã Phú Giáo');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Xã Phước Thành');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Xã An Long');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Xã Phước Hòa');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Phường Tân Uyên');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Phường Tân Khánh');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Xã Bắc Tân Uyên');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Xã Thường Tân');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Phường Vĩnh Tân');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Phường Bình Cơ');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Phường Tân Hiệp');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Phường Dĩ An');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Phường Tân Đông Hiệp');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Phường Đông Hòa');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Phường Lái Thiêu');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Phường Thuận Giao');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Phường An Phú');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Phường Thuận An');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Phường Bình Hòa');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Phường Vũng Tàu');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Phường Tam Thắng');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Phường  Rạch Dừa');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Phường Phước Thắng');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Xã Long Sơn');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Phường Bà Rịa');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Phường Long Hương');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Phường Tam Long');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Xã Ngãi Giao');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Xã Xuân Sơn');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Xã Bình Giã');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Xã Châu Đức');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Xã Kim Long');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Xã Nghĩa Thành');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Xã Hồ Tràm');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Xã Xuyên Mộc');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Xã Bàu Lâm');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Xã Hòa Hội');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Xã Hòa Hiệp');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Xã Bình Châu');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Xã Long Điền');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Xã Long Hải');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Xã Đất Đỏ');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Xã Phước Hải');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Phường Phú Mỹ');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Phường Tân Hải');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Phường Tân Phước');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Phường Tân Thành');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Xã Châu Pha');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Đặc khu Côn Đảo');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Phường Tân Định');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Phường Sài Gòn');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Phường Bến Thành');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Phường Cầu Ông Lãnh');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Phường An Phú Đông');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Phường Thới An');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Phường Tân Thới Hiệp');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Phường Trung Mỹ Tây');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Phường Đông Hưng Thuận');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Phường Linh Xuân');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Phường Tam Bình');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Phường Hiệp Bình');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Phường Thủ Đức');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Phường Long Bình');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Phường Tăng Nhơn Phú');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Phường Phước Long');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Phường Long Phước');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Phường Long Trường');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Phường  An Nhơn');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Phường An Hội Đông');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Phường An Hội Tây');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Phường Gò Vấp');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Phường Hạnh Thông');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Phường Thông Tây Hội');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Phường Bình Lợi Trung');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Phường Bình Quới');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Phường Bình Thạnh');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Phường Gia Định');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Phường Thạnh Mỹ Tây');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Phường Tân Sơn Nhất');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Phường Tân Sơn Hòa');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Phường Bảy Hiền');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Phường Tân Hòa');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Phường Tân Bình');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Phường Tân Sơn');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Phường Tây Thạnh');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Phường Tân Sơn Nhì');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Phường Phú Thọ Hòa');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Phường Phú Thạnh');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Phường Tân Phú');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Phường Đức Nhuận');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Phường Cầu Kiệu');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Phường Phú Nhuận');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Phường An Khánh');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Phường Bình Trưng');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Phường Cát Lái');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Phường Xuân Hòa');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Phường Nhiêu Lộc');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Phường Bàn Cờ');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Phường Hòa Hưng');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Phường Diên Hồng');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Phường Vườn Lài');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Phường Hòa Bình');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Phường Phú Thọ');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Phường Bình Thới');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Phường Minh Phụng');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Phường Xóm Chiếu');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Phường Khánh Hội');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Phường Vĩnh Hội');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Phường Chợ Quán');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Phường An Đông');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Phường Chợ Lớn');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Phường Phú Lâm');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Phường Bình Phú');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Phường Bình Tây');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Phường Bình Tiên');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Phường Chánh Hưng');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Phường Bình Đông');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Phường Phú Định');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Phường Bình Hưng Hòa');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Phường Bình Tân');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Phường Bình Trị Đông');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Phường Tân Tạo');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Phường An Lạc');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Phường Tân Hưng');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Phường Tân Thuận');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Phường Phú Thuận');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Phường Tân Mỹ');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Xã Tân An Hội');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Xã An Nhơn Tây');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Xã Nhuận Đức');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Xã Thái Mỹ');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Xã Phú Hòa Đông');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Xã Bình Mỹ');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Xã Củ Chi');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Xã Hóc Môn');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Xã Đông Thạnh');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Xã Xuân Thới Sơn');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Xã Bà Điểm');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Xã Tân Nhựt');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Xã Vĩnh Lộc');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Xã Tân Vĩnh Lộc');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Xã Bình Lợi');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Xã Bình Hưng');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Xã Hưng Long');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Xã Bình Chánh');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Xã Nhà Bè');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Xã Hiệp Phước');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Xã Cần Giờ');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Xã Bình Khánh');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Xã An Thới Đông');
INSERT INTO `communes` (`provinceID`, `name`) VALUES (2, 'Xã Thạnh An');