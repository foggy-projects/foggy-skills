---
name: mysql-docker-client
description: Execute MySQL operations through Docker container client. Use when you need to: (1) Execute SQL queries or modifications on remote MySQL databases, (2) Run DDL statements (CREATE/ALTER/DROP tables), (3) Execute SQL script files, (4) Export query results, (5) Perform database migrations or bulk operations. Supports both single SQL commands and batch file execution.
---

# MySQL Docker Client

Execute MySQL operations through a Docker-based MySQL client without installing MySQL locally.

## Quick Start

### Execute Single SQL Query

```bash
python scripts/execute_sql.py \
  --host <host> \
  --port <port> \
  --user <username> \
  --password <password> \
  --database <database> \
  --sql "SELECT * FROM users LIMIT 10"
```

### Execute SQL File

```bash
python scripts/execute_sql_file.py \
  --host <host> \
  --port <port> \
  --user <username> \
  --password <password> \
  --database <database> \
  --file path/to/script.sql
```

### Export Query Results

```bash
python scripts/export_data.py \
  --host <host> \
  --port <port> \
  --user <username> \
  --password <password> \
  --database <database> \
  --sql "SELECT * FROM orders WHERE date > '2026-01-01'" \
  --output results.csv \
  --format csv
```

## Connection Security

**IMPORTANT**: Never hardcode credentials. Always accept connection info as parameters from the user.

## Docker Container

The skill uses a persistent MySQL client container (`mysql-client-skill`):
- **Auto-start**: Container starts automatically when scripts run
- **Persistent**: Container stays running for repeated use
- **Network**: Uses host network mode for external database access
- **Image**: Official MySQL 8.0 with full client tools

Manual container management (optional):
```bash
# Start container manually
cd docker && docker-compose up -d

# Stop container
cd docker && docker-compose down

# Check container status
docker ps | grep mysql-client-skill
```

The scripts automatically ensure the container is running before executing commands.

## Common Operations

See [references/mysql-operations.md](references/mysql-operations.md) for:
- DDL templates (CREATE/ALTER TABLE)
- Data migration patterns
- Index management
- Common troubleshooting

## Error Handling

Scripts exit with non-zero codes on failure. Check:
1. Network connectivity to MySQL host
2. Credentials validity
3. Database/table existence
4. SQL syntax

## Output Formats

- `csv`: CSV with headers (default for exports)
- `json`: JSON array of objects
- `table`: Plain text table (console output)
