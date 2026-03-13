#!/usr/bin/env bash
# Check frpc service status and recent logs on remote server
set -euo pipefail
source "$(dirname "$0")/common.sh"
load_env

echo "=== frpc status on ${FRPC_SSH_HOST} ==="

# Try systemctl status first, fallback to ps
eval "$(ssh_cmd)" "systemctl status frpc 2>/dev/null || (echo '--- Process list ---' && ps aux | grep frpc | grep -v grep)" || true

echo ""
echo "=== Recent logs (last 30 lines) ==="
eval "$(ssh_cmd)" "journalctl -u frpc -n 30 --no-pager 2>/dev/null || tail -n 30 /var/log/frpc.log 2>/dev/null || echo 'No logs found via journalctl or /var/log/frpc.log'"
