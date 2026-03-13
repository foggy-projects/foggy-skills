#!/usr/bin/env bash
# Pull frpc config from remote server to local temp file
set -euo pipefail
source "$(dirname "$0")/common.sh"
load_env

LOCAL_FILE="/tmp/frpc_config_remote"
echo "Pulling ${FRPC_CONFIG_PATH} from ${FRPC_SSH_HOST}..."
eval "$(scp_cmd pull "$LOCAL_FILE")"
echo "OK: Config saved to ${LOCAL_FILE}"
echo "---"
cat "$LOCAL_FILE"
