#!/usr/bin/env bash
# Push local frpc config back to remote server
set -euo pipefail
source "$(dirname "$0")/common.sh"
load_env

LOCAL_FILE="/tmp/frpc_config_remote"
if [[ ! -f "$LOCAL_FILE" ]]; then
  echo "ERROR: Local config file not found at ${LOCAL_FILE}"
  echo "Run pull.sh first, then edit the file."
  exit 1
fi

echo "Pushing config to ${FRPC_SSH_HOST}:${FRPC_CONFIG_PATH}..."

# Backup remote config first
eval "$(ssh_cmd)" "cp ${FRPC_CONFIG_PATH} ${FRPC_CONFIG_PATH}.bak.$(date +%Y%m%d%H%M%S)" 2>/dev/null || true

eval "$(scp_cmd push "$LOCAL_FILE")"
echo "OK: Config uploaded successfully."
