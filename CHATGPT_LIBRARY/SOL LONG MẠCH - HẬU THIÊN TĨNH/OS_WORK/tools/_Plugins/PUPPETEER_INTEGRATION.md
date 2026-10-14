# Puppeteer — tích hợp vào SOL-LONG-MACH

Nguồn chính xác: https://github.com/puppeteer/puppeteer.git
Commit nguồn ghim: `d1b9a2162a0113356db5093f055b4a2e1979c6a8`.
Loại: Git submodule, tại `CHATGPT_LIBRARY/SOL LONG MẠCH - HẬU THIÊN TĨNH/OS_WORK/tools/_Plugins/puppeteer` trên nhánh `main` của `2708halinh-cloud/SOL-LONG-MACH`.
Giấy phép nguồn: Apache-2.0.

## Nhận mã nguồn đầy đủ sau khi clone

```sh
git submodule update --init --recursive
```

## Xác minh gitlink

```sh
git ls-tree HEAD "CHATGPT_LIBRARY/SOL LONG MẠCH - HẬU THIÊN TĨNH/OS_WORK/tools/_Plugins/puppeteer"
```

Kết quả phải có mode `160000` và SHA `d1b9a2162a0113356db5093f055b4a2e1979c6a8`.

## Sử dụng trong dự án JavaScript

Puppeteer là thư viện điều khiển Chrome/Firefox, không phải plugin ChatGPT độc lập hoặc MCP server tự chạy.

```sh
npm install puppeteer
# Hoặc nếu muốn sử dụng trình duyệt đã cài sẵn:
npm install puppeteer-core
```

Tài liệu chính thức: https://pptr.dev/docs
Upstream README giới thiệu MCP: https://github.com/ChromeDevTools/chrome-devtools-mcp

Trạng thái: mã nguồn đã gắn dưới dạng submodule; không có lệnh cài dependency, chạy chương trình hay đăng ký MCP được thực thi trong bước này. Không thay đổi skill Anatomy và các plugin hiện hữu.
