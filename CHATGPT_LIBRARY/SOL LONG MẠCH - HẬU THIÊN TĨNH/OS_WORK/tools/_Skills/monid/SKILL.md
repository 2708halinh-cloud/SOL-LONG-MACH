---
name: monid
description: Truy cập danh mục công cụ dữ liệu Monid qua MCP hoặc CLI sau khi kiểm tra xác thực, schema và chi phí.
---
# Monid — nguồn ưu tiên

Nguồn nguyên bản: https://monid.ai/SKILL.md
Phiên bản nguồn quan sát: 0.1.7 (2026-10-18).

Quy trình: kiểm tra MCP Monid đã kết nối → khám phá công cụ → xem schema và chi phí → chỉ thực thi khi có quyền và điều kiện phù hợp → kiểm chứng kết quả. Ưu tiên công cụ đã kết nối của SOL; không tự thay thế bằng tuyến có phí. Nếu MCP chưa hoạt động, kiểm tra CLI trên host được ủy quyền. Không đưa khóa hay token vào mã nguồn, phản hồi hoặc nhật ký.

Tệp này là cầu định tuyến trong SOL; để tra quy trình Monid mới nhất, đọc SKILL.md chính chủ. Việc có tệp không chứng minh Monid đã được cài trong ChatGPT hoặc xác thực qua OAuth.
