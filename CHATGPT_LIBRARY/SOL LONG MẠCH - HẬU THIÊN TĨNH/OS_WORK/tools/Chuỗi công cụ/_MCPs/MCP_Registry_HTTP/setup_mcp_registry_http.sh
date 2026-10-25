#!/usr/bin/env bash
# Chuẩn bị/xác thực tên miền với MCP Registry qua HTTP (Ed25519).
# Không ghi khóa riêng vào web root, Git hoặc bản ghi DNS.
set -Eeuo pipefail
umask 077

ACTION="${1:-}"
DOMAIN="${2:-}"
WEB_ROOT="${3:-.}"

if [[ "$ACTION" != "prepare" && "$ACTION" != "login" ]] || [[ ! "$DOMAIN" =~ ^[A-Za-z0-9]([A-Za-z0-9.-]*[A-Za-z0-9])?$ ]]; then
  printf 'Dùng:\n  bash %s prepare gambbrazil.fun /path/to/public-web-root\n  bash %s login gambbrazil.fun\n' "$0" "$0" >&2
  exit 1
fi

KEY_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/mcp-publisher/keys/$DOMAIN"
KEY_FILE="$KEY_DIR/ed25519.pem"
PUBLIC_URL="https://$DOMAIN/.well-known/mcp-registry-auth"

if [[ "$ACTION" == "prepare" ]]; then
  mkdir -p "$KEY_DIR" "$WEB_ROOT/.well-known"
  chmod 700 "$KEY_DIR"
  if [[ ! -e "$KEY_FILE" ]]; then
    openssl genpkey -algorithm Ed25519 -out "$KEY_FILE"
    chmod 600 "$KEY_FILE"
  fi
  PUBLIC_KEY="$(openssl pkey -in "$KEY_FILE" -pubout -outform DER | tail -c 32 | base64 | tr -d '\r\n')"
  printf 'v=MCPv1; k=ed25519; p=%s\n' "$PUBLIC_KEY" > "$WEB_ROOT/.well-known/mcp-registry-auth"
  chmod 644 "$WEB_ROOT/.well-known/mcp-registry-auth"
  printf 'Đã tạo file công khai: %s\n' "$WEB_ROOT/.well-known/mcp-registry-auth"
  printf 'Khóa riêng nằm tại: %s (không được công bố)\n' "$KEY_FILE"
  printf 'Cần triển khai file công khai thành: %s\n' "$PUBLIC_URL"
  printf 'Khi đã triển khai, dùng: bash %s login %s\n' "$0" "$DOMAIN"
  exit 0
fi

if [[ ! -s "$KEY_FILE" ]]; then
  echo "Chưa có khóa riêng tại $KEY_FILE. Chạy prepare trước." >&2
  exit 2
fi
if ! command -v mcp-publisher >/dev/null 2>&1; then
  echo "Chưa cài mcp-publisher trong môi trường hiện tại." >&2
  exit 3
fi

EXPECTED="$(openssl pkey -in "$KEY_FILE" -pubout -outform DER | tail -c 32 | base64 | tr -d '\r\n')"
ACTUAL="$(curl -fLsS --max-time 20 "$PUBLIC_URL" | tr -d '\r\n')"
if [[ "$ACTUAL" != "v=MCPv1; k=ed25519; p=$EXPECTED" ]]; then
  echo "HTTPS readback không trùng với khóa công khai hiện tại; chưa đăng nhập." >&2
  exit 4
fi

PRIVATE_KEY="$(openssl pkey -in "$KEY_FILE" -noout -text | grep -A3 'priv:' | tail -n +2 | tr -d ' :\n')"
if [[ ${#PRIVATE_KEY} -ne 64 ]]; then
  unset PRIVATE_KEY
  echo "Khóa Ed25519 không đủ 64 ký tự hex; dừng." >&2
  exit 5
fi
mcp-publisher login http --domain "$DOMAIN" --private-key "$PRIVATE_KEY"
unset PRIVATE_KEY
