---
name: frpc-remote-manage
description: "Remote frpc (frp client) configuration management via SSH. Pull, edit, push config and restart frpc service on remote servers. Use when: (1) user wants to modify frpc proxy config, (2) add/remove/edit frpc proxy rules, (3) check frpc status, (4) restart frpc service, (5) user mentions 'frpc', 'frp', 'reverse proxy config', or '/frpc'."
---

# frpc Remote Config Management

Manage frpc configuration on remote servers via SSH scripts. Supports both `.ini` and `.toml` formats.

## Prerequisites

Ensure `sshpass` is installed if using password auth: `apt install sshpass` or `brew install sshpass`.

## Setup

Check if `.env` exists in the skill directory. If not, copy from `assets/.env.example` and ask user to fill in:

```bash
cp assets/.env.example .env
```

Then prompt user to edit `.env` with their SSH and frpc details.

All scripts below run from the skill directory: `cd /home/sa/.claude/skills/frpc-remote-manage`

## Workflow

Execute these steps in order:

### 1. Pull current config

```bash
bash scripts/pull.sh
```

This downloads remote config to `/tmp/frpc_config_remote`. Read this file to understand current config.

### 2. Edit config locally

Read `/tmp/frpc_config_remote`, apply user's requested changes, write back to the same path.

**For .ini format** - sections like:
```ini
[proxy_name]
type = tcp
local_ip = 127.0.0.1
local_port = 8080
remote_port = 9090
```

**For .toml format** - sections like:
```toml
[[proxies]]
name = "proxy_name"
type = "tcp"
localIP = "127.0.0.1"
localPort = 8080
remotePort = 9090
```

Preserve existing proxies unless user explicitly asks to remove them.

### 3. Push config back

```bash
bash scripts/push.sh
```

This automatically creates a timestamped backup on the remote server before overwriting.

### 4. Restart frpc

```bash
bash scripts/restart.sh
```

### 5. Verify status

```bash
bash scripts/status.sh
```

Check output for errors. If frpc failed to start, read the logs, diagnose the issue, and fix the config.

## Quick Status Check

If user only wants to check status (no config change), run `scripts/status.sh` directly.

## Rollback

If something goes wrong, the backup file on the remote server is at `{FRPC_CONFIG_PATH}.bak.{timestamp}`. SSH in and restore it.
