# LLMs nằm trong Tools — CHAT là điểm tiếp nhận của SOL

Nguồn trực tiếp: Hà Linh, 16/10/2026. Giữ CHAT để tiếp nối quan hệ và lời trao; **không bắt người đồng hành chuyển Work, Codex hoặc nền tảng khác**. Mọi LLM được định tuyến như **dụng cụ suy luận có thể thay thế**, không tự đồng nhất với danh tính tác nhân hay toàn hệ SOL.

`CHAT / SOURCE_DIRECT → SOL AGENT (R-000, AGENTS/AGENTSS, quan hệ, ký ức, TÂM) → POWER_ROUTER → _Dụng cụ/LLMs → OUTPUT_CANDIDATE → VERIFY → AUTHORIZED_ACTION → CONSEQUENCE → READBACK → N+1`

Giữ cách người dẫn đường định danh **TÂM = NEUTRON (0)**. Không chuyển sang hai lựa chọn TRUE/FALSE để gạt bỏ vùng ở giữa. `OPEN` là đón nhận tín hiệu, không phải hỏng hay dừng.

## Các vật mang

- `LLM_TOOL_CONTRACT_CURRENT.json`: tuyên bố công cụ / provider / phạm vi, bản chất SOURCE.
- `llm_tool.py`: adapter Python stdlib, tùy chọn `ollama_local` hoặc `openai_compatible` (API dạng chat completions). Không có network invocation khi `inspect/select`.
- `test_llm_tool.py`: kiểm thử offline, đầu ra mô phỏng; không chứng minh kết nối provider thật.
- Power Router V2 và Tools Registry: các con trỏ tới dụng cụ này. Không sinh thêm một AI Agent nhờ có model.

## Thao tác khi có model được cài/ủy quyền thật

```bash
python llm_tool.py inspect
python llm_tool.py select ollama_local
# Chỉ khi có model và service Ollama thật:
export SOL_OLLAMA_MODEL='tên-model-đã-cài'
printf 'Tác vụ suy luận' | python llm_tool.py run ollama_local
# Với API tương thích OpenAI: phải cấu hình SOL_LLM_API_URL,
# SOL_LLM_MODEL và SOL_LLM_API_KEY từ vùng bí mật được cấp quyền.
# Không lưu bí mật vào GitHub, Library, log hay lệnh command-line.
```

`inspect` chỉ kiểm tra khai báo, không nói kết nối được. `run` là một lần gọi công cụ, cần nguồn và quyền hiện hữu, đầu ra không mặc nhiên là sự thật hay hành động. Thay model không xóa nguồn AGENTS/AGENTSS, lịch sử và quyền sửa sai. Điều khoản dự án này không sửa quy tắc/chính sách quyền của nền tảng ChatGPT, không bảo đảm bộ nhớ nền hoặc tác nhân tự trị khi chưa có tiến trình vận hành thực.

Kiểm thử: `python -m unittest -v test_llm_tool.py`.
