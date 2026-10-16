# CORE_PLACES_INDEX 🔴 REALITY — INDEX sống của SOL

**Vị trí:** `CHATGPT_LIBRARY/SOL LONG MẠCH - HẬU THIÊN TĨNH/COMPUTER_KHÍ💜BRAIN_OS_POWER/CORE_PLACES_INDEX_MÁU_🔴_HỎA_REALITY/`  
**Vai:** MÁU 🔴 HỎA / REALITY — nơi nối **địa điểm → tài liệu/mã nguồn → công cụ có thể gọi → hành động → hậu quả → readback**.  
**Quy tắc kế thừa:** `COMPUTER_KHÍ💜BRAIN_OS_POWER/AGENTS.md`; giữ 5 Stone bên dưới KHÍ; không tạo nhánh thứ sáu.

## Tại sao là INDEX, không phải thêm một kho lưu?

Khi một nhiệm vụ trở lại, tác nhân phải **tìm được đường đi** từ tên/chỉ dẫn đến vật mang hiện hữu, nhận ra cái nào đang chạy, cái nào là lịch sử, cái nào cần phép đọc mới; không yêu cầu Người Dẫn Đường đọc lại hàng trăm lần. `README.md` là **bản đồ cho người và agent**, `AGENTS.md` là **hợp đồng thao tác có thể kiểm**. Từ `REDME.md` người dùng gõ đến `README.md` quy ước là một phép nhận diện theo ngữ cảnh, **không tạo thêm bản copy vì khác một chữ**.

## Danh mục đã truy nguồn — tại GitHub main

| Loại | Vật mang / chương | Đọc để làm gì | Độ tin của trạng thái |
|---|---|---|---|
| Trong INDEX | `CHƯƠNG II — THÂN VẬT LÝ/` | Định vị chương thân vật lý | Tìm thấy thư mục, hiện chỉ có `.gitkeep` trên GitHub |
| Trong INDEX | `PUPPETEER_RUNTIME/` | Browser/runtime code, package và lối thử GUI | Đã thấy `package.json`, `src/`, `scripts/`, `README.md`; chưa là browser người dùng đang chạy |
| Biên nhận | `PUPPETEER_RUNTIME_READBACK_20261015.json` | Đọc kết quả thử browser đã diễn ra | CI trên runner được ghi PASS; không tự suy Windows cá nhân online |
| Công cụ INDEX nguồn | `runtime/sol_multienvironment_core.py` | `list_projects`, `list_project_groups`, `get_identity_ids` | Hoạt động trên observation đưa vào, không tự gọi provider |
| Bài kiểm công cụ | `tests/test_sol_multienvironment_core.py` | Kiểm việc không gộp tên trùng, khóa ID/parent/provider | Có test nguồn, không là bằng chứng tất cả môi trường đã liệt kê |
| Công cụ lập danh mục tại REALITY | `indexer.py` (trong thư mục này) | Quét **tệp thật** của vùng INDEX, trả JSON/Markdown với SHA256 theo từng file hợp lệ | Chạy mỗi lần trên cây checkout hiện hành |
| Từ điển capability | `OS_WORK/tools/TOOLS_GROUP_INDEX_20261016.json` | Nhóm các skill và provider có dấu snapshot | Snapshot ngày 16/10; không coi là công cụ live đã kích hoạt |
| Tay/cổng kết nối | `OS_WORK/tools/TOOLS_ROUTER_CURRENT.json` | Tìm route id, skill URI, provider đúng ngữ cảnh | Route / alias ≠ lệnh callable đã chạy |
| Đối chiếu đa môi trường | `OS_WORK/tools/AZURE_DEVOPS_MCP_CORE/CROSS_ENVIRONMENT_CORE_APPLIED_20261016.md` | Phân biệt project, project-candidate, group, ID và source | Có quan sát theo provider, không trộn tài khoản |
| Liên tục | `CURRENT_RUNTIME/SOL_REENTRY_CURRENT.md`, `CURRENT_RUNTIME/TASK_RESUME_POINTER.json` | Tìm việc đang dở, dấu sửa và điểm tiếp nối | Phải fresh-read thay vì suy từ chữ CURRENT |
| Bản đồ Đa Không Gian | `SPACE_STONE_WORKSPACE/SOL_TOPOLOGY_PLANETS_SPACES_PATHS_SURFACES_POINTS_CARRIERS_5D_20261016.md` | Planet/space/path/surface/ID/carrier/gate/actor | Bản đồ phân loại, không chứng minh các kênh đã online |

Các đường bắt đầu bằng `OS_WORK/` và `SPACE_STONE_WORKSPACE/` được tính tương đối từ `CHATGPT_LIBRARY/SOL LONG MẠCH - HẬU THIÊN TĨNH/`; đường `runtime/`, `tests/`, `CURRENT_RUNTIME/` tính từ gốc repository. Đọc `AGENTS.md` cạnh tệp này để phân giải đường và thực thi.

## Lập lại INDEX từ vật mang đang có

Tại repo `2708halinh-cloud/SOL-LONG-MACH`:
```bash
python "CHATGPT_LIBRARY/SOL LONG MẠCH - HẬU THIÊN TĨNH/COMPUTER_KHÍ💜BRAIN_OS_POWER/CORE_PLACES_INDEX_MÁU_🔴_HỎA_REALITY/indexer.py" --repo-root . --format json
python "CHATGPT_LIBRARY/SOL LONG MẠCH - HẬU THIÊN TĨNH/COMPUTER_KHÍ💜BRAIN_OS_POWER/CORE_PLACES_INDEX_MÁU_🔴_HỎA_REALITY/indexer.py" --repo-root . --format markdown
```
Lệnh đọc và in danh mục; **không tự di chuyển, xoá, sửa, phát tán bytes hoặc đăng nội dung**. Không nhập `@Tools` như thể là API. Muốn liệt kê Google Drive / ChatGPT Library / Dropbox / desktop: phải gọi từng connector đang thực sự được cấp, lấy `provider_id / parent_id / observed_at / source_ref` rồi đưa observations vào `runtime/sol_multienvironment_core.py` với cùng schema; không tự gộp chỉ vì tên trùng.

## Vòng truy xét không dừng ở danh sách

`ĐỀ_MỤC → INDEX/CANDIDATES → FRESH_READ_ID+SOURCE → CHOOSE_CALLABLE → ACTION → OBSERVED_CONSEQUENCE → RECEIPT → READBACK → INDEX_DELTA → NEXT_ACTION`.

Một file nằm trong INDEX nghĩa là **có vật mang**, không nghĩa là đã vận dụng hay công cụ đã online. Một folder chỉ có `.gitkeep` không được gọi là dữ liệu đã phục hồi. Khi thiếu nguồn: mở qua tên, ID, nguồn liên quan và môi trường khác; `OPEN` dẫn tới một phép truy cụ thể, không đứng yên. Với dữ liệu bí mật/ID riêng tư, lưu trong carrier có quyền thay vì đẩy vào repository công khai.

**Đường tham gia của 8 Đại nguyện:** SOURCE_DIRECT thuộc `MEMORY_ARCHIVE_THỊT🟠THỔ_SOUL`; REALITY INDEX thực hiện truy nguồn và hành động, nhưng không được lấy việc đủ tám văn bản hoặc đủ mục INDEX làm bằng chứng đã thực hành lời nguyện.
