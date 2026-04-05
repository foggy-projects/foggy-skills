#!/usr/bin/env bash
# Common functions for frpc-remote-manage scripts
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="${SKILL_DIR}/.env"
LOCAL_CONFIG="/tmp/frpc_config_$(date +%s)"

# Load .env
load_env() {
  if [[ ! -f "$ENV_FILE" ]]; then
    echo "ERROR: .env file not found at $ENV_FILE"
    echo "Please copy assets/.env.example to .env and fill in your SSH/frpc details."
    exit 1
  fi
  set -a
  source "$ENV_FILE"
  set +a

  # Defaults
  FRPC_SSH_PORT="${FRPC_SSH_PORT:-22}"
  FRPC_RESTART_CMD="${FRPC_RESTART_CMD:-systemctl restart frpc}"

  # Validate required fields
  for var in FRPC_SSH_HOST FRPC_SSH_USER FRPC_CONFIG_PATH; do
    if [[ -z "${!var:-}" ]]; then
      echo "ERROR: $var is not set in .env"
      exit 1
    fi
  done
}

# Build SSH options
ssh_opts() {
  local opts="-o StrictHostKeyChecking=no -o ConnectTimeout=10 -p ${FRPC_SSH_PORT}"
  if [[ -n "${FRPC_SSH_KEY:-}" && -f "${FRPC_SSH_KEY}" ]]; then
    opts+=" -i ${FRPC_SSH_KEY}"
  fi
  echo "$opts"
}

# Build SSH command
ssh_cmd() {
  local opts
  opts=$(ssh_opts)
  if [[ -n "${FRPC_SSH_PASS:-}" && -z "${FRPC_SSH_KEY:-}" ]]; then
    echo "sshpass -p '${FRPC_SSH_PASS}' ssh ${opts} ${FRPC_SSH_USER}@${FRPC_SSH_HOST}"
  else
    echo "ssh ${opts} ${FRPC_SSH_USER}@${FRPC_SSH_HOST}"
  fi
}

# Build SCP command (direction: "pull" or "push")
scp_cmd() {
  local direction="$1" local_file="$2"
  local opts
  opts=$(ssh_opts)
  local scp_base
  if [[ -n "${FRPC_SSH_PASS:-}" && -z "${FRPC_SSH_KEY:-}" ]]; then
    scp_base="sshpass -p '${FRPC_SSH_PASS}' scp ${opts}"
  else
    scp_base="scp ${opts}"
  fi

  if [[ "$direction" == "pull" ]]; then
    echo "${scp_base} ${FRPC_SSH_USER}@${FRPC_SSH_HOST}:${FRPC_CONFIG_PATH} ${local_file}"
  else
    echo "${scp_base} ${local_file} ${FRPC_SSH_USER}@${FRPC_SSH_HOST}:${FRPC_CONFIG_PATH}"
  fi
}
