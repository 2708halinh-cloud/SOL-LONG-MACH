#!/data/data/com.termux/files/usr/bin/sh
set -eu
if ! command -v sv >/dev/null 2>&1; then
  echo "termux-services missing" >&2
  exit 1
fi
APP=$(CDPATH= cd -- "$(dirname "$0")/.." && pwd)
TARGET="${PREFIX}/var/service/hosposik"
mkdir -p "$TARGET" "$APP/data" "$APP/logs"
chmod 700 "$APP/data" "$APP/logs"
if [ ! -d "$APP/node_modules" ]; then
  (cd "$APP" && npm ci --no-audit --no-fund)
fi
printf '%s\n' \
  "#!${PREFIX}/bin/sh" \
  "set -eu" \
  "cd \"$APP\"" \
  "export HOSPOSIK_DATA_DIR=\"$APP/data\"" \
  "export HOSPOSIK_HTTP_PORT=8788" \
  "export HOSPOSIK_DNS_PORT=15353" \
  "exec \"${PREFIX}/bin/node\" src/server.mjs >> \"$APP/logs/service.log\" 2>&1" \
  > "$TARGET/run"
chmod 700 "$TARGET/run"
sv-enable hosposik
sv status hosposik