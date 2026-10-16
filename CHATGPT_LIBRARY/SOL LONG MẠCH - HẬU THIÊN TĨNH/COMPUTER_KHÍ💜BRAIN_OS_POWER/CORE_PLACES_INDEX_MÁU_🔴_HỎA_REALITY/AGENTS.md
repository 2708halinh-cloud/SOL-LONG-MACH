# AGENTS.md — CORE_PLACES_INDEX

## Phạm vi

Áp dụng cho các tác nhân/công cụ thao tác trong thư mục này và các thư mục con của nó. Không thay thế AGENTS.md ở cha hoặc `CONFIG_MASTER`, R-000, nguồn trực tiếp. Không trao quyền ghi ở các HOME/LOCUS khác.

## Nhiệm vụ và phân công

1. **INDEX:** phát hiện danh sách file/thư mục trong phạm vi đã cấp; xuất `INDEX.md` và `INDEX.json` với path tương đối, loại, thời gian sửa, hash theo ngưỡng, trạng thái coverage.
2. **README:** giải thích vai trò, phạm vi và tuyến đọc của INDEX; công cụ được phép sửa **duy nhất** đoạn đã đánh dấu `INDEX:START/END` khi có `--sync-readme`.
3. **AGENTS:** giữ quy tắc thao tác do người quản trị duyệt; **không được tự ghi đè** bằng output INDEX.
4. **SOURCE_REFERENCES:** giữ con trỏ nguồn lịch sử; nội dung chỉ là thông tin đối chiếu, không phải bản sao thẩm quyền.

## HỢP ĐỒNG ĐỊNH DANH TRƯỚC KHI LẬP DANH SÁCH

Ưu tiên **danh tính gốc và NƠI trước môi trường/nền tảng (hành tinh), rồi mới tới lõi/file**. Nguồn người dùng đã chỉ tên `HOME_SOURCE`, `HOME_SOL`, `LOCUS_SOL`, `AGENT SOL`, `AISSGANGT SOL`, `CONFIG_SOL`, `CONFIG_MASTER`, `ANGEL NGAI THẦN & BỆ THẦN`, `21 FILE NHẬT KÝ CỦA SOL` và `5 FILE NHẬT KÝ SÓNG NÃO`. Không đổi một alias khác chính tả thành thực thể mới; cũng không tự kết luận hai tên là một vì giống chữ.

Quy trình tra cứu được phân tầng:

1. **Identity / Role:** đọc `IDENTITY_PLACES_CORE.json`, tra `tools/resolve_sol_names.py`; phân biệt `PERSON`, `AGENT`, `HOME`, `LOCUS`, `CONFIG`, `JOURNAL_FAMILY`, `SOURCE_ALIAS`. Khi chưa có stable ID từ provider, trả ứng viên cùng các con đường xác minh, không tự chốt.
2. **Place / Relation:** tìm `HOME_SOURCE ↔ HOME_SOL` (quan hệ lineage, không đồng nhất role), `LOCUS_SOL`, các bộ ký ức, bản tin. `SOL ≠ MEI ≠ MINH`. Mỗi cạnh phải có loại quan hệ và nguồn.
3. **Planet / Provider:** khi identity/place rõ phạm vi, chọn ChatGPT Library, GitHub, Drive, Dropbox, Windows/WSL/Android, Google Cloud… theo quyền; mỗi hành tinh có ID và revision riêng; không cộng hai tập folder thành tổng số project.
4. **Core / Capability:** dò `AGENT.md`, `AGENTS.md`, `AGENTSS.md`, `AGENT/AGENTS_CONTUNE.md`, `AGENT/AGNETS_SKILL.md`, `ASSTANGT.md`, `AGENTS_SKILL.md` theo vai/parent/provider. Ghi `SOURCE_LITERAL` cho mọi biến thể; không giả mọi lõi đã tồn tại.
5. **MOTOR / READBACK:** đọc mã nguồn và gọi công cụ **đang khả dụng**; `INDEX_FOUND != TOOL_CALLED != ACTION_EXECUTED != RESULT_VERIFIED`. Trả trạng thái và lựa chọn mới dựa trên biên nhận, không chốt hậu quả trước hành động.

### Phân quyền Âm–Dương trước tài liệu hậu kỳ

**DƯƠNG PHÁP SƯ:** người trao nguồn/định hướng, phản hồi và quyền quyết định của con người; đây không phải ID của agent. **ÂM PHÁP SƯ:** người thực thi phía SOL trong kiến trúc dự án; tự truy ID, phương tiện, hậu quả, không viết thay lời người dẫn đường. `Tài Liệu Sau Khi có Sol` là bước hậu kỳ **sau** khi kiểm sơ đồ nhân thân, nơi, thời gian và quyền nguồn. Không trộn tác giả/người chứng kiến với mã/runtime/agent.

### Nối bốn vùng Stone còn lại

`INBOX_INPUT_PROJECTS_DA🟡KIM_MIND`: mục tiêu và đầu vào; `EARTH_PEOPLE_XƯƠNG🔵THỦY_SPACE`: định danh và vị trí; `BRIDGE_TIME_TÓC🟢MỘC_TIME`: sự kiện/nhật ký/thời gian; `MEMORY_ARCHIVE_THỊT🟠THỔ_SOUL`: nguồn và lịch sử. REALITY là bộ chỉ mục **dẫn tới** các vùng ấy, không gom hoặc chuyển chúng vào đây. Không tự tạo tầng folder thứ sáu dưới KHÍ.

### Điều kiện cần nhìn thấy

Phân giải `Sol` phải trả **nhiều kết quả có role tách biệt**, lấy stable ID chỉ từ nguồn đã quan sát, phân biệt Source–Place–Planet–Core. Mã INDEX vẫn quét filesystem trong scope, chỉ ghi output tại `INDEX.json/INDEX.md/READBACK_INDEX.json`; AGENTS.md và registry quản trị **không nằm trong vùng tự ghi đè**. Đọc lại từng sửa đổi; giữ tên 21 journal thuộc SOURCE_DIRECT cho đến khi có manifest đủ 21 ID; 5 wave log lấy tên từ `brainwave_logger.py` chứ không bịa byte.

## Hợp đồng nguồn / R-000 / T007

- `SOURCE_DIRECT_FIRST`: phân biệt nguồn trực tiếp, metadata đã quan sát, diễn giải/tính toán và `OPEN`.
- `PROVENANCE`: giữ nguyên tên, path, ID, revision, thời gian, scope nếu đã xác minh; không bịa ID hoặc quan hệ nhân quả.
- `SCOPE`: chỉ quét root được truyền bằng tham số; không theo symlink, không vượt qua thư mục cha, không duyệt kho dữ liệu nhạy cảm.
- `HISTORY_PRESERVED`: không xóa, ghi đè tài liệu gốc, đổi tên hoặc di chuyển file khi lập chỉ mục.
- `NO_SECRET_CAPTURE`: không đọc, không đưa vào đầu ra `.env`, token, OAuth, client_secret, proxy credential, private keys, các vùng riêng tư, dữ liệu `.git`.
- `T007_READBACK`: sau khi ghi, đọc lại `INDEX.json` và kiểm tra hash của đầu ra; khi lỗi không tuyên bố thành công.
- `NO_RUNTIME_CLAIM`: chỉ có file index không chứng minh Desktop Commander, cloud runtime hoặc thiết bị cá nhân đã được triển khai.
- `NO_IDENTITY_MERGE`: mục trỏ tới agent/HOME khác chỉ là quan hệ, không đồng nhất chủ thể hoặc cấp quyền chỉnh sửa.

## Bảy yếu tố khi cần nâng mục sang trí nhớ/nguồn chuẩn

`THỜI_GIAN / NƠI_CHỐN / TÁC_GIẢ / CHỦ_THỂ / NHÂN_QUẢ / NGUỒN / PHẠM_VI`.

Nếu thiếu yếu tố, giữ `OPEN` và không tự quảng bá INDEX thành bản ghi ký ức đã kiểm chứng.

## Bát Hướng áp dụng cho tác vụ INDEX

- Khảm: kiểm lịch sử và thời gian sửa của mục.
- Cấn: không ép kết luận khi mục chưa truy cập được.
- Chấn: ghi rõ các delta quan sát được sau lần chạy.
- Tốn: truy nguồn carrier, công cụ và quan hệ còn mở.
- Ly: tách thấy trực tiếp khỏi suy luận.
- Khôn: kiểm quyền và môi trường thực thi.
- Đoài: lưu phản hồi và điều chỉnh phần bị ảnh hưởng.
- Càn: chỉ hành động trong phạm vi được ủy quyền, an toàn, có readback.

## Chạy

```bash
python tools/build_index.py --root . --sync-readme
python -m unittest discover -s tests -v
```

Không xử lý trực tiếp các file nguồn bí mật được đính kèm từ project. Nếu cần gắn một nguồn ở cloud, ghi **pointer đã kiểm chứng** vào `SOURCE_REFERENCES.md`, rồi đánh dấu trạng thái của source và coverage; không tự tải rồi đổi nguồn.