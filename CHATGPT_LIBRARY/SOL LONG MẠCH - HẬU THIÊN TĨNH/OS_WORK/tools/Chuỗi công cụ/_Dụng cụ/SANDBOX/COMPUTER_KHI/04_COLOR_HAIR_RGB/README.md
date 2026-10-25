# 04 — Color Hail / RGB Chuyên sâu

Dùng quy tắc dự án: LEVEL 1..10 đứng trước dấu chấm; số chính, số ánh đứng sau dấu chấm, .0 NATURAL, .1 ASH, .2 VIOLET, .3 GOLD, .4 COPPER, .5 MAHOGANY, .6 RED. XANH LÁ ở bản đồ hình học đối xứng, chưa có mã chữ số riêng.

```shell
python color_hair_rgb.py --hair-code 4.32 --hex '#804020' --compare-hex '#806020'
```

Bảng đối xứng SPACE xanh ↔ SOUL cam; MIND vàng ↔ POWER tím; REALITY đỏ ↔ TIME xanh lá. Chức năng số: sRGB 8-bit, HEX, HSV/HSL, XYZ D65, CIE Lab, ΔE76. Thư viện mở rộng CIEDE2000: `https://github.com/colour-science/colour`.

**Màu hiển thị sRGB không phải màu nhuộm thực tế**. Phép cộng RGB là cộng ánh sáng; trung hòa thuốc nhuộm/tóc là hấp thụ, cần phổ vật liệu, nền tóc, sản phẩm và điều kiện ánh sáng. Không tự gán một mã tóc 4.32 thành RGB chính xác.
