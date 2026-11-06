#!/usr/bin/env bash
set -Eeuo pipefail
if (( EUID != 0 )); then
  echo '请使用 root 权限运行：sudo bash install.sh' >&2
  exit 1
fi
command -v python3 >/dev/null || { echo '缺少 python3' >&2; exit 1; }
SOURCE="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)/hy2hop.py"
[[ -f "$SOURCE" ]] || { echo '缺少 hy2hop.py，请下载完整项目' >&2; exit 1; }
python3 -m py_compile "$SOURCE"
exec python3 "$SOURCE" "$@"
