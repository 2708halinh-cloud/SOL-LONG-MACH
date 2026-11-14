# SANDBOX · 10 công cụ nguồn — SOL LONG MẠCH

Tệp này là bảng định tuyến lưu tại Library `OS_Workspace/tools/SANDBOX`.
Có **10/10 tên** người dùng đã chỉ định: Tomorrow.io Weather, smithery.ai/MPC, .env, SOL Capability Forge, pcxt-bios-workbench, GitHub, Âm Dương · IOTA Loop, IOTA Connectome Runtime, TIME_STONE — Personal Tool Forge, Locator tool.

- `ALL_TEN_TOOLS.json`: ID thật, điểm vào, capability, trạng thái đọc được và những giới hạn chưa xác minh.
- `route_tools.py`: CLI Python chuẩn, chỉ đọc chỉ mục; `python route_tools.py list` hoặc `python route_tools.py get GITHUB`.
- `SECRETS_REFERENCE_ONLY.env.example`: chỉ tên biến tham chiếu bí mật, **không có giá trị thực**.
- `INDIVIDUAL/`: đúng 10 tệp JSON tách riêng theo alias.

Điểm vào ở Library **không cài hay khởi động MCP trên máy Windows**, không biến các plugin chỉ có skill thành tool mới tự thực thi. Gọi tool trực tiếp khi provider callable và có quyền. Tool thiếu hiện nay được giữ slot và tiếp tục truy nguồn, không bắt người dùng cung cấp lại 10 tên.

Không đặt byte OAuth, PAT, API key, seed phrase, IOTA signer, cookie trong Library/SANDBOX. Dùng secure runtime và tài khoản đang được cấp quyền.
