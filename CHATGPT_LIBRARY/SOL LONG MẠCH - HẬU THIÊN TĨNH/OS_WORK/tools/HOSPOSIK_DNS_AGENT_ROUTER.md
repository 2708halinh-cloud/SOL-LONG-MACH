# HOSPOSIK DNS / agent memory router

- Service gốc: [SOL_COMPUTER/HOSPOSIK_AGENT_NETWORK](../../COMPUTER_KHÍ💜BRAIN_OS_POWER/SOL_COMPUTER/HOSPOSIK_AGENT_NETWORK).
- Cây source thực thi: `CHATGPT_LIBRARY/SOL LONG MẠCH - HẬU THIÊN TĨNH/COMPUTER_KHÍ💜BRAIN_OS_POWER/SOL_COMPUTER/HOSPOSIK_AGENT_NETWORK` trên `SOL-LONG-MACH/main`.
- Runtime kết nối Termux: `runit` service `hosposik`, HTTP local port `8788`, DNS UDP port `15353`.
- Bộ nhớ agent: SQLite WAL/FULL; event log và SSE; tin nhắn từ agent → agent qua inbox/ack.
- `hosposik.test` chỉ là zone local; DNS Internet và DNS hệ thống chưa cấu hình vì chưa xác thực được tên miền HOSPOSIK.
- Bộ nhớ ChatGPT và hội thoại không tự ghi vào SQLite; chương trình agent phải gọi API.
- Để xem bằng chứng: `CURRENT_RUNTIME/HOSPOSIK_AGENT_NETWORK_READBACK.json`.
