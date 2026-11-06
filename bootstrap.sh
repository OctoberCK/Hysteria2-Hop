#!/usr/bin/env bash
set -Eeuo pipefail
if (( EUID != 0 )); then
  echo '请使用 root 权限运行' >&2
  exit 1
fi
command -v curl >/dev/null || { echo '缺少 curl' >&2; exit 1; }
command -v python3 >/dev/null || { echo '缺少 python3' >&2; exit 1; }
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
curl -fL --retry 3 --connect-timeout 10 -o "$TMP/hy2hop.py" 'https://raw.githubusercontent.com/OctoberCK/Hysteria2-Hop/main/hy2hop.py'
python3 -m py_compile "$TMP/hy2hop.py"
python3 "$TMP/hy2hop.py" "$@"
