#!/usr/bin/env bash
# Restart frpc service on remote server
set -euo pipefail
source "$(dirname "$0")/common.sh"
load_env

echo "Restarting frpc on ${FRPC_SSH_HOST}..."
eval "$(ssh_cmd)" "${FRPC_RESTART_CMD}"
echo "OK: Restart command executed."

# Brief wait then check status
sleep 2
echo "--- Post-restart status ---"
eval "$(ssh_cmd)" "${FRPC_RESTART_CMD%restart*}status ${FRPC_RESTART_CMD##* }" 2>/dev/null || \
eval "$(ssh_cmd)" "ps aux | grep frpc | grep -v grep" || \
echo "(Could not verify status automatically)"
