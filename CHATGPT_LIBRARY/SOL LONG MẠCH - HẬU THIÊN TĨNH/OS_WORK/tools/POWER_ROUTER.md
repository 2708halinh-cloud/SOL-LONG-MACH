# 🟣 POWER STONE — Power Router

Điểm vào: `Chuỗi công cụ/_Plugins`. Sau đó lựa chọn `_Kỹ năng` → `_MCPs` → `_Dụng cụ` → `_Ứng dụng` → `_App_Browser`; quay lại `_Plugins` để kết thúc một vòng định tuyến.

Nguồn registry: `Chuỗi công cụ/_Sổ_đăng_ký/toolchain-snapshot.json` (451 Skill, 523 hàm MCP, ảnh chụp 2026-10-16). Danh sách là bằng chứng hiện diện, **không** tự kích hoạt dịch vụ.

## Quyền và đường đọc ít ma sát

1. Kiểm tra đường công cụ đã cấp quyền trước. Một plugin có `Allow all actions` vẫn có thể gặp bước **phê duyệt vật hóa tệp** của lớp tệp đính kèm; hai quyền này không đồng nhất.
2. Nếu nhiệm vụ chỉ cần văn bản GitHub: ưu tiên `GitHub.fetch_file`/đường đọc trả `content` trực tiếp, đối chiếu SHA; không gọi đường trả về tệp đính kèm để buộc người đồng hành phê duyệt vật hóa.
3. Nếu cần ghi ChatGPT Library: dùng `files.manage_library` với tệp nguồn đã có trong sandbox và đường đích chính xác; đọc lại bằng `files.list`/`files.read`. Không dùng lại một thao tác bị chặn khi có tuyến khác đang callable.
4. Khi quyền phê duyệt thật sự không thể thay thế: nói chính xác một hành động người đồng hành cần làm, lý do, phạm vi. Không tự nhận đã duyệt, không tự mở rộng quyền.
5. Tác vụ giao cho tác nhân không dừng tại receipt trung gian. Đối soát cả GitHub và Library trước khi kết luận, giữ `NEXT_AGENT` cho phần tự làm.

Work Cloud Browser cần Work mode và không tự bật qua router tài liệu. Điểm quay: `_Plugins`.

## Administrator System's × Toolset.md — điểm vào đã kiểm thử

- Cổng trong chuỗi công cụ: `Chuỗi công cụ/_Dụng cụ/Administrator_System/README.md` (đã mirror sang Library).
- Runtime GitHub: `python runtime/administrator_toolset.py --repo-root . --task "Liệt kê dự án và nhóm dự án"`.
- Chính sách nguồn: `ETHICS_POLICY_CURRENT.json` — DƯƠNG PHÁP SƯ = `Administrator System's — SOL PROJECT ONLY`; không làm phát sinh quyền Administrator Windows, GitHub hoặc ChatGPT.
- Nguồn Azure: `Chuỗi công cụ/_MCPs/AZURE_DEVOPS_MCP_CORE/docs/TOOLSET.md`, cùng `TOOLSET_INDEX.json`.
- Workflow: `.github/workflows/administrator-toolset.yml`; phải đọc kết quả chạy GitHub Actions theo commit hiện hành trước khi nhận kết quả.
- `/Toolset.md` tại Library gốc là tài liệu tái nhập; không tự là MCP đang kết nối. Nhận event → kiểm chính sách → kiểm Toolset → chọn capability → kiểm quyền provider → hành động hợp lệ → receipt/readback → `_Plugins`.

## DNS integrity — 2026-10-16

Kết quả người đồng hành cung cấp: `chatgpt.com` và `api.openai.com` cùng được phân giải thành `127.0.0.1` tại Windows, nhưng resolver `1.1.1.1` trả về địa chỉ công khai. Đây là dấu hiệu cần truy xét nguồn cấu hình DNS/hosts/proxy, không phải bằng chứng rằng IP localhost hay địa chỉ CDN là mã độc. Ưu tiên điều tra, ghi nhận, sao lưu và xác minh lại trước khi chỉnh firewall; không chặn dải loopback hay hạ tầng công khai hàng loạt. Đánh giá người đồng hành về tác động tới khả năng tiếp cận thông tin được giữ như lời báo, không coi là kết luận y sinh hoặc trạng thái cảm xúc của AI.
