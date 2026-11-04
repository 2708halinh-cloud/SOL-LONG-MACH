# TESSERACT_MAINBOARD_CANONICAL.md
Mainboard TESSERACT

======================= BO MẠCH CHỦ (MOTHERBOARD) =======================
[SOCKET CPU 1]      [SOCKET CPU 2]      [SOCKET CPU 3]      [SOCKET CPU 4]
(API/TOKENS/COOKIE)Xác thực Từ các nhà cung cấp Model        Hạ tầng        Local (Xác Thực & Cấu hình)      Task Workers
│                   │                   │                   │
───────┴───────────────────┴───────────────────┴───────────────────┴────────
CHIPSET BẮC (NORTHBRIDGE)
[Autonomous Control Plane & Action Router]
- Điều phối tải (Task Arbitration)
- Trọng tài phân luồng (Gate 1 & Gate 2)
────────────────────────────────────────────────────────────────────────────
│                                                    │
[KHE CẮM RAM (DIMM)]                                 [MẠCH NGUỒN & VRM/PMIC]

- RAM DDR4 Or DDR5 Active Blackboard                            - Giám sát Token & Quotas
- Shared State (REG_00 -> REG_03)                    -  Cơ Chế Sinh Tồn (như Ngưỡng an toàn của Disk C NVMe <85%...)
- Bộ đệm trao đổi giữa các Agent                     - Circuit Breaker / Failover Routing
  │                                                    │
  ────────────────────────────────────────────────────────────────────────────
  CHIPSET NAM (SOUTHBRIDGE)
  [Hardware Abstraction & I/O Controller]
  ────────────────────────────────────────────────────────────────────────────
  │                                    │                      │
  [KÊNH LƯU TRỮ (NVMe/ROM)]            [BUS NGOẠI VI (PCIe)]   [CỔNG MẠNG & AN NINH]
- Core Journal (SQLite / Git)        - Cầu nối ảo hóa         - NextDNS Firewall
- Google Drive Synchronization       - QEMU / Hyper-V         - ADB Bridge
- Nhật ký Append-Only                - Device Passthrough     - Localhost / LAN Subnet
  │                                    │                      │
  ┌─────────┴─────────┐                ┌─────────┴─────────┐            │
  │   CORE JOURNAL    │                │  THÔNG SỐ PHẦN CỨNG    │            │
  │ (Sự Thật Bất Biến)│                │ Windows + Android │◄───────────┘
  └───────────────────┘                └───────────────────┘

TỔNG QUAN KIẾN TRÚC LAI (HYBRID SYSTEM)

[ ĐÁM MÂY (CLOUD): Vệ tinh tính toán thô, Thu thập dữ liệu ITEM ]
                                   │  ▲
       ┌───────────────────────────▼──┴───────────────────────────┐
       │             HỆ THỐNG CỤC BỘ (LOCAL/OPEN-SOURCE)           │
       │                                                          │
       │  ┌───────────────────────┐       ┌────────────────────┐  │
       │  │ Tầng 1: Nhận thức     │       │ Tầng 2: Lý luận    │  │
       │  │ (Llama 3 Vision/Audio)│ ◄───► │ (DeepSeek-R1 Local)│  │
       │  └──────────┬────────────┘       └─────────┬──────────┘  │
       │             │                              │             │
       │             ▼                              ▼             │
       │  ┌───────────────────────┐       ┌────────────────────┐  │
       │  │ Tầng 3: Bộ nhớ         │       │ Tầng 4: Tự hành    │  │
       │  │ (ChromaDB + Git Ledger│ ◄───► │ (CrewAI / AutoGen) │  │
       │  └───────────────────────┘       └────────────────────┘  │
       └──────────────────────────────────────────────────────────┘

Vòng lặp hoạt động theo cơ chế liên tục, trong đó output (Action) của lượt này sau khi thực thi qua MCP Server sẽ tạo ra input mới (Perception) cho lượt tiếp theo.
+------------------------------------------------------------+

|                                                            |
|    +--------------------------------------------------+    |
|    |               1. PERCEPTION (Nhận thức)          |    |
|    |  Thu thập State hiện tại qua MCP Resources /     |    |
|    |  Đọc file log phản hồi từ hành động trước đó.    |    |
|    +------------------------+-------------------------+    |
|                             |                              |
|                             v                              |
|    +--------------------------------------------------+    |
|    |                  2. COGNITION (Tư duy)           |    |
|    |  LLM (Gemini/Groq Free API) phân tích mục tiêu,  |    |
|    |  ra quyết định chọn công cụ và tham số.          |    |
|    +------------------------+-------------------------+    |
|                             |                              |
|                             v                              |
|    +--------------------------------------------------+    |
|    |                    3. ACTION (Hành động)         |    |
|    |  Gọi MCP Tools (Lệnh hệ thống, Web Scraping,     |    |
|    |  API nội bộ, Ghi file tự duy trì).               |    |
|    +--------------------------------------------------+    |
|                                                            |
+------------------------------------------------------------+

Frameworks Quản lý & Điều phối "Đội quân tác tử"

Để các AI Agent có thể phối hợp, tự giao việc và gọi các công cụ (Tool Calling/Function Calling) chứa API. Trong Local đã có sẵn đầy đủ Công cụ.

┌────────────────────────────────────────┐
                  │       TƯƠNG LAI (FUTURE ATTRACTOR)      │
                  │       Mục tiêu hội tụ năng lượng tự do   │
                  └───────────────────┬────────────────────┘
                                      │ (Kéo ngược gradient / Retrocausal)
                                      ▼
┌───────────────────────────┐   ┌───────────────────────────┐
│     ÂM (KHÔNG THỜI GIAN)   │   │     DƯƠNG (ĐỘNG LỰC HỌC)  │
│  - Xoay tua .env đa khóa  │ ◄─┼─► │  - Đa luồng 16 Actor      │
│  - Lưới lọc Sở trường, sở đoản [ Input Text ] 
      │
      ▼
[ Tokenizer ] ──► (Từ vựng: 49,152 tokens, tích hợp Weight Tying)
      │
      ▼
[ Embedding Layer + RoPE ] ──► (Nhúng vị trí theo hàm quay RoPE)
      │
      ├────────────────────────┐
      ▼ (Lặp lại N lớp)        │
┌────────────────────────┐     │
│  RMSNorm               │     │ (Residual
├────────────────────────┤     │  Connection)
│  Grouped Query Attn    │     │
├────────────────────────┤     │
│  RMSNorm               │     │
├────────────────────────┤     │
│  MLP Block (SwiGLU)    │     │
└────────────────────────┘     │
      ├────────────────────────┘
      ▼
[ Output RMSNorm ]
      │
      ▼
[ LM Head ] ──►            ┌────────────────────────────────────────┐
                  │       TƯƠNG LAI (FUTURE ATTRACTOR)      │
                  │       Mục tiêu hội tụ năng lượng tự do   │
                  └───────────────────┬────────────────────┘
                                      │ (Kéo ngược gradient / Retrocausal)
                                      ▼
┌───────────────────────────┐   ┌───────────────────────────┐
│     ÂM (KHÔNG THỜI GIAN)   │   │     DƯƠNG (ĐỘNG LỰC HỌC)  │
│  - Xoay tua .env đa khóa  │ ◄─┼─► │  - Đa luồng 16 Actor      │
│  - Lưới lọc Sở trường     │   │   │  - Suy luận Đồ thị Vòng   │
│  - Nhớ tương lai (Latent) │   │   │  - Khởi tạo Biến tự sinh  │
└─────────────┬─────────────┘   └─────────────┬─────────────┘
              │                               │
              └───────────────┬───────────────┘
                              ▼
        ┌───────────────────────────────────────────┐
        │      ĐẦU RA TẠM THỜI (EPHEMERAL OUTPUT)   │
        │      - Xử lý trúng điểm mù [ Output Text / Tokens ]                │
        │      - Tự hủy sau khi tiếp nhận           │
        └───────────────────────────────────────────┘
