#!/usr/bin/env bash
# Safe, opt-in tmpfs cache. Does not move profiles, secrets or persistent data.
# Usage as root: bash setup-linux-tmpfs-cache.sh /mnt/ramdisk/sol_chrome_cache 512
set -Eeuo pipefail
target=/mnt/ramdisk/sol_chrome_cache
size_mb=512
if (( $# >= 1 )); then target="$1"; fi
if (( $# >= 2 )); then size_mb="$2"; fi
[[ "$size_mb" =~ ^[0-9]+$ ]] || { echo 'SIZE_MUST_BE_INTEGER_MB' >&2; exit 2; }
(( size_mb >= 64 && size_mb <= 2048 )) || { echo 'SIZE_OUT_OF_RANGE_64_TO_2048' >&2; exit 2; }
[[ "$target" == /mnt/ramdisk/* ]] || { echo 'TARGET_NOT_IN_DEDICATED_RAMDISK_NAMESPACE' >&2; exit 2; }
[[ ! -L "$target" ]] || { echo 'SYMLINK_TARGET_FORBIDDEN' >&2; exit 2; }
if command -v findmnt >/dev/null 2>&1 && findmnt -rn --mountpoint "$target" >/dev/null 2>&1; then
  fs="$(findmnt -rn -o FSTYPE --mountpoint "$target")"
  [[ "$fs" == tmpfs ]] || { echo 'TARGET_ALREADY_MOUNTED_NON_TMPFS' >&2; exit 2; }
  echo "EXISTING_TMPFS_VERIFIED $target"
  exit 0
fi
if [[ -d "$target" ]] && [[ -n "$(ls -A "$target")" ]]; then
  echo 'EXISTING_NONEMPTY_FOLDER_REFUSED; do not cover existing files with tmpfs' >&2
  exit 2
fi
free_kib="$(awk '/MemAvailable:/ {print $2}' /proc/meminfo)"
[[ -n "$free_kib" ]] || { echo 'MEMAVAILABLE_NOT_OBSERVED' >&2; exit 2; }
(( free_kib >= (size_mb + 1024) * 1024 )) || { echo 'INSUFFICIENT_AVAILABLE_MEMORY' >&2; exit 2; }
(( EUID == 0 )) || { echo 'ROOT_REQUIRED_FOR_MOUNT; no changes made' >&2; exit 2; }
mkdir -p -- "$target"
mount -t tmpfs -o "size=$size_mb""m,mode=0700,nosuid,nodev" tmpfs "$target"
[[ "$(findmnt -rn -o FSTYPE --mountpoint "$target")" == tmpfs ]] || { echo 'MOUNT_READBACK_FAILED' >&2; exit 3; }
printf 'RAM_TMPFS_READY path=%s max_mb=%s volatile=yes persistent_profile_unchanged=yes\n' "$target" "$size_mb"
