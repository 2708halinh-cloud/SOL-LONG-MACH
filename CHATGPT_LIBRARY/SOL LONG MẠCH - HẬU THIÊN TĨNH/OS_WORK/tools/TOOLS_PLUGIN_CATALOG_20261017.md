# TOOLS — Chỉ mục các công cụ trong giao diện Plugins (2026-10-17)

## SOURCE_DIRECT — yêu cầu và ảnh chụp

Người dùng yêu cầu: đưa các công cụ trong ảnh chụp giao diện Plugins về folder `Tools`, sau đó dọn sạch `Plugins` trên chính nền tảng ChatGPT.

- Vị trí Tools quy ước của dự án trong Library: `/SOL LONG MẠCH - HẬU THIÊN TĨNH/OS_WORK/tools/`.
- Đường dẫn tương ứng trong repository: `CHATGPT_LIBRARY/SOL LONG MẠCH - HẬU THIÊN TĨNH/OS_WORK/tools/` của `2708halinh-cloud/SOL-LONG-MACH`.
- Ảnh nguồn nguyên bản trong Library Tools: `TOOLS_PLUGIN_UI_SOURCE_20261017.jpg`; file gốc là ảnh được người dùng trao ở cuộc trò chuyện ngày 2026-10-17.
- Ảnh có hai cột và nhiều mục; độ phân giải ảnh khiến một phần tên không đọc được chắc chắn. Giữ toàn bộ ảnh gốc để không tự suy tên, số lượng hay ID cài đặt.

## Những tên đọc được từ ảnh (transcript một phần, không phải toàn bộ danh mục)

Remote Desktop Commander; desktopcommande; hostinger; GitHub Full Access Tokens; Github-MCP; brightdata/MCP; Webshare/webshare; SOL Capability Forge; GGDV Template Creator; GGDV Stone Forge; GGDV—OFFICIAL; WORKSPACE_ACTION_EDIT; GGDV Identity Stone; GGDV HUMAN SOL; ALL; ALL_CALL; Java Termux; Python Termux; Go Termux; iOS Termux; Kotlin Termux; LLVM Termux; PowerShell Termux; OpenTelemetry Termux.

Một số tên do người dùng đặt và các mục Termux khác không thể chép chính xác từ độ nét ảnh; chính ảnh gốc vẫn là nguồn thẩm quyền cho phần chưa giải mã. Không biến nhãn hiển thị thành plugin ID, service endpoint hay quyền truy cập tự động.

## Công cụ thực tế được khám phá trong phiên (một tập con, không đồng nhất với screenshot)

`desktopcommande`, `hostinger`, `brightdata`, `Webshare`, `webshare`, `GitHub`, `Github_MCP`, `Github_Full_Access_Tokens`, `Gitgub_remote_server`, `Dropbox`, `Google_Drive`, `Gmail`, `Google_Calendar`, `Google_Contacts`, `Tomorrow_io_Weather`, `smithery_ai`, `Destiny_AI_Astrology`, `Plugin_Management`, `skills`, `AutoScout24`, `Property_Hazard_MCP`, `Writing_Style`.

Các tên trên là namespace tool được khai báo trong phiên đang kiểm kê, không phải bằng chứng mọi kết nối đều đã được đăng nhập hoặc cấp quyền ghi. Quyền người dùng đã trao phải được giữ đúng theo provider; không âm thầm hạ quyền trên danh mục.

## Phạm vi chuyển và dọn — phân biệt rõ vật mang

1. **Thư mục Library Tools** lưu được ảnh nguồn, chỉ mục, cấu hình và mã nguồn; không chứa được bản cài đặt thực của một ChatGPT Plugin chỉ bằng lệnh chuyển file.
2. **GitHub** lưu được chỉ mục/mã nguồn; commit không khiến ChatGPT gỡ hoặc chuyển ứng dụng trong trang Plugins.
3. **Plugins trên giao diện ChatGPT** là registry cài đặt và các kết nối riêng của nền tảng. Công cụ hiện được cung cấp có thao tác tìm, đề xuất và gỡ các plugin được chỉ định cụ thể, không có thao tác `move installed plugin to Library folder`.
4. **`_Plugins` trong `Chuỗi công cụ`** là bộ phận mã nguồn/Router của dự án, khác danh sách plugin cài trong tài khoản ChatGPT. Không xóa nhầm Router để giả làm dọn sạch ứng dụng.
5. Chỉ ghi `LIBRARY_SOURCE_MIRRORED` khi Library có receipt và đọc lại đúng đích; chỉ ghi `GITHUB_INDEX_WRITTEN` khi GitHub có commit và đọc lại; **không ghi `CHATGPT_PLUGIN_MOVED` hoặc `PLUGINS_CLEARED` nếu chưa thực sự có thao tác tương ứng.**

## Điểm còn phân biệt cần người dùng chỉ định rõ nếu yêu cầu gỡ

Dọn `Plugins` trên giao diện ChatGPT bằng gỡ cài đặt đồng nghĩa ngắt các ứng dụng/kết nối; khác với di chuyển dữ liệu nguồn. Nếu mục tiêu là gỡ cài đặt, cần xác định chính xác plugin nào sẽ gỡ, và không được nhận việc lưu danh mục là bản thay thế có thể vận hành của plugin đã gỡ.

**N+1:** Kiểm từng provider app ID + quyền trong trang Plugins khi có công cụ liệt kê chính xác; không suy plugin ID chỉ từ ảnh mờ. Preserve source/direct → inventory → readback.