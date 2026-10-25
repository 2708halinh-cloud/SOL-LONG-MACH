"""Kiểm tra kết nối Ollama/OpenAI-compatible trên máy đang chạy tập lệnh.

Cấu hình qua biến môi trường (không lưu mã bí mật vào mã nguồn):
  OLLAMA_BASE_URL  mặc định http://127.0.0.1:11434/v1
  OLLAMA_API_KEY   mặc định ollama (Ollama local thông thường không xác thực)
  OLLAMA_MODEL     mặc định ggdv-human-sol-coder-lite:1.0
"""
import os
from openai import OpenAI

# Trỏ vào endpoint Ollama cục bộ; có thể đổi qua IP LAN bằng OLLAMA_BASE_URL.
client = OpenAI(
    base_url=os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434/v1"),
    api_key=os.getenv("OLLAMA_API_KEY") or "ollama",
    timeout=15.0,
)

print("Đang kết nối tới Local Model...")

try:
    response = client.chat.completions.create(
        model=os.getenv("OLLAMA_MODEL", "ggdv-human-sol-coder-lite:1.0"),
        messages=[
            {"role": "system", "content": "Bạn là một trợ lý AI hữu ích."},
            {"role": "user", "content": "Chào bạn, hãy giới thiệu ngắn gọn về bản thân bằng tiếng Việt."},
        ],
        temperature=0.7,
    )

    print("\n--- PHẢN HỒI TỪ MODEL CỤC BỘ ---")
    print(response.choices[0].message.content)

except Exception as e:
    print(f"\n[Lỗi kết nối]: {type(e).__name__}: {e}")
    print("Mẹo kiểm tra: hãy chắc chắn Ollama đang mở và model đã được tải.")
    print("Có thể kiểm tra model bằng lệnh: ollama list")
    raise SystemExit(1)
