# CHORME TÁC NHÂN — Chrome DevTools Protocol độc lập

Tuyến này là **mã nguồn điều khiển Chromium/Chrome có CDP**, không phụ thuộc Desktop Commander, Microsoft login, Dropbox, Hostinger hoặc 2Captcha. Không yêu cầu sao chép token hay mật khẩu vào chương trình.

## Đã chạy thật

Ngày 11/10/2026: đã chạy thử nghiệm trên Chromium headless qua cổng debug cô lập `19222`: kết nối, đọc tab, nhấn nút `Input.dispatchMouseEvent`, nhập văn bản `Input.insertText`, hậu kiểm `Runtime.evaluate` và chụp ảnh `Page.captureScreenshot`. Ảnh cùng tập lệnh kiểm thử được giữ riêng.

Thử nghiệm này **không chứng minh kết nối tới trình duyệt Windows của Hà Linh**. Cổng `192.168.1.12:9222` chưa truy cập được từ môi trường thực thi này; `9222` trên PC cần được xác nhận từ bên trong PC hoặc qua một đường hầm riêng có xác thực. Không mở CDP ra mạng công cộng.

## Cài trên đúng máy đang chạy Chrome debug

Yêu cầu: Python 3.10+ và gói `websocket-client`.

```
python -m pip install -r requirements.txt
python chorme_agent.py --port 9222 status
python chorme_agent.py --port 9222 tabs
python chorme_agent.py --port 9222 click "#my-button"
python chorme_agent.py --port 9222 type "#my-input" "Nội dung kiểm thử"
python chorme_agent.py --port 9222 read "#status"
python chorme_agent.py --port 9222 screenshot screenshot.png
```

Đối chiếu phiên nguồn đúng theo `DevToolsActivePort`, dùng thêm `--expect-browser /devtools/browser/<browser-uuid>`; không tự chấp nhận một browser khác để thao tác vào nhầm tài khoản.

### Khởi tạo Chrome nếu chưa bật CDP

Trên Windows, Chrome mới có thể yêu cầu thư mục hồ sơ debug riêng. Không đóng Chrome đang dùng hay đưa mật khẩu vào câu lệnh; chỉ mở phiên debug bằng hồ sơ riêng nếu phiên có sẵn không truy cập được.

```
"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-address=127.0.0.1 --remote-debugging-port=9222 --user-data-dir="%TEMP%\chrome-agent-profile"
```

Lưu ý: hồ sơ mới không tự đăng nhập tài khoản cũ. `--remote-debugging-port` chỉ dùng trên máy em/đường hầm tin cậy; tuyệt đối không chuyển tiếp công khai cổng 9222.

## Đối chiếu nguồn và quyền

- `192.168.1.12` được cung cấp như địa chỉ shortcut LAN; chưa xác minh nó chạy CDP hoặc chia sẻ dữ liệu.
- Vật mang VHDX `G:\OS_Workspace\TESSERACT_OS\TESSERACT Hard Disk.vhdx` **chưa bị chỉnh sửa**.
- Mã nguồn đang lưu ở môi trường triển khai và Library (khi có kết quả upload riêng), **không có chứng cứ đã cài vào máy Windows**.
- Các trường mật khẩu Microsoft, mật khẩu PC, Bearer token, Dropbox, WebContainer API hoặc OAuth **không được chép vào repo hoặc tệp log**.

## Trạng thái

`CDP_LOCAL_TEST=PASS` · `HOST_PC_CDP=OPEN` · `VHDX_WRITE=NO` · `BRAIN_PLUGIN_RELEASE=UNMODIFIED`.


## CHOERME ACCOUNT = C: — AccountBookmarks source

Đã nạp tín hiệu AccountBookmarks với hai bookmark mục tiêu: `ChatGPT - SOL` và `Sign in | FUNiX`. File được gửi qua chat; `AccountBookmarks_SOURCE_DIRECT_EXCERPT.json` là **trích nguồn giới hạn** (không gồm `sync_metadata`), không được nhận nhầm là bản sao nguyên vẹn từ Chrome trên Windows. Không suy luận người dùng đã đăng nhập tài khoản JINEY từ bookmark.

Câu lệnh trên đúng máy Windows đang có Chrome (không cần mật khẩu):

```
python chorme_agent.py bookmarks --match SOL
python chorme_agent.py --port 9222 status
python chorme_agent.py --port 9222 open-bookmark --guid e1715471-a294-4e3d-889a-7a1f5416b319
```

`--profile-directory "Profile 1"` đổi profile; `--bookmarks-path <path>` dùng một bản nguồn được chỉ rõ. Mặc định đọc `AccountBookmarks` trong `Default` thuộc `%LOCALAPPDATA%\Google\Chrome\User Data`. Lệnh `bookmarks` chỉ đọc file. `open-bookmark` tạo tab mới, không đụng tab hiện hành và chỉ chấp nhận GUID khớp đúng một bookmark.

Bài kiểm thử `test_account_bookmarks.py` và `test_open_bookmark_cdp.py` đạt; Chromium cô lập tạo được tab từ bookmark và đọc lại DOM offline. **Tải URL HTTP của trang thử nghiệm không được xác minh**, cũng không có tác động lên Chrome Windows, tài khoản Google, SOL raw chat hoặc VHDX.
