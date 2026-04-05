# MySQL Docker Client Skill - 使用说明

## 技能概述

这是一个全局技能，允许通过 Docker MySQL 客户端连接和操作远程 MySQL 数据库，无需本地安装 MySQL。

## 安装技能

将 `mysql-docker-client.skill` 文件安装到 Claude Code:

```bash
# 技能文件位置
C:\Users\oldse\.claude\skills\mysql-docker-client.skill
```

## 前置要求

1. **Docker** 已安装并运行
2. **Python 3.6+** （用于执行脚本）
3. **网络访问** 到目标 MySQL 数据库

## 使用示例

### 1. 执行单条 SQL 查询

```bash
python scripts/execute_sql.py \
  --host 192.168.1.100 \
  --port 3306 \
  --user root \
  --password yourpassword \
  --database mydb \
  --sql "SELECT * FROM users LIMIT 10"
```

### 2. 执行 SQL 文件

```bash
python scripts/execute_sql_file.py \
  --host 192.168.1.100 \
  --port 3306 \
  --user root \
  --password yourpassword \
  --database mydb \
  --file /path/to/migration.sql
```

### 3. 导出查询结果

导出为 CSV:
```bash
python scripts/export_data.py \
  --host 192.168.1.100 \
  --port 3306 \
  --user root \
  --password yourpassword \
  --database mydb \
  --sql "SELECT * FROM orders WHERE created_at > '2026-01-01'" \
  --output orders.csv \
  --format csv
```

导出为 JSON:
```bash
python scripts/export_data.py \
  --host 192.168.1.100 \
  --user root \
  --password yourpassword \
  --database mydb \
  --sql "SELECT id, name, email FROM users" \
  --output users.json \
  --format json
```

### 4. 常见数据库操作

**添加字段:**
```bash
python scripts/execute_sql.py \
  --host <host> --user <user> --password <pass> --database <db> \
  --sql "ALTER TABLE users ADD COLUMN phone VARCHAR(20) AFTER email"
```

**创建索引:**
```bash
python scripts/execute_sql.py \
  --host <host> --user <user> --password <pass> --database <db> \
  --sql "CREATE INDEX idx_email ON users(email)"
```

**批量更新:**
```bash
python scripts/execute_sql.py \
  --host <host> --user <user> --password <pass> --database <db> \
  --sql "UPDATE orders SET status = 'completed' WHERE status = 'finished'"
```

## 在 Claude Code 中使用

当你向 Claude 提问时，技能会自动触发：

**示例 1 - 查询数据:**
```
User: 帮我查询 MySQL 中 users 表的前 10 条记录
      数据库信息: host=192.168.1.100, user=root, password=xxx, database=mydb

Claude: [自动使用 mysql-docker-client 技能执行查询]
```

**示例 2 - 执行 DDL:**
```
User: 在 orders 表中添加 delivery_time 字段，类型为 TIMESTAMP
      连接信息: [提供连接参数]

Claude: [使用技能执行 ALTER TABLE 语句]
```

**示例 3 - 数据导出:**
```
User: 导出所有 2026 年的订单数据到 CSV 文件
      MySQL: host=xxx, user=xxx, password=xxx, database=xxx

Claude: [使用 export_data.py 导出数据]
```

## Docker 容器管理

技能使用持久化的 MySQL 客户端容器 (`mysql-client-skill`)：

**自动管理:**
- 脚本首次运行时自动启动容器
- 容器保持运行状态供后续使用
- 无需手动启动或停止

**手动管理 (可选):**
```bash
# 启动容器
cd docker && docker-compose up -d

# 停止容器
cd docker && docker-compose down

# 查看容器状态
docker ps | grep mysql-client-skill

# 查看容器日志
docker logs mysql-client-skill
```

## 参考文档

详细的 MySQL 操作参考见：
- `references/mysql-operations.md` - DDL 模板、数据迁移模式、索引管理

## 安全提示

- ❌ 不要在代码中硬编码密码
- ✅ 每次手动提供连接信息
- ✅ 在生产环境执行前先在测试环境验证
- ✅ 重要操作前先备份数据

## 故障排查

**Docker 未运行:**
```
Error: Cannot connect to the Docker daemon
→ 启动 Docker Desktop
```

**网络无法访问:**
```
Error: Can't connect to MySQL server
→ 检查防火墙、网络连接和主机地址
```

**权限不足:**
```
Error: Access denied for user
→ 检查用户名、密码和数据库权限
```

## 技能文件结构

```
mysql-docker-client/
├── SKILL.md                          # 技能定义
├── docker/
│   └── docker-compose.yml           # MySQL 客户端容器配置
├── scripts/
│   ├── docker_utils.py              # Docker 容器管理工具
│   ├── execute_sql.py               # 执行单条 SQL
│   ├── execute_sql_file.py          # 执行 SQL 文件
│   └── export_data.py               # 导出数据
└── references/
    └── mysql-operations.md          # MySQL 操作参考
```

---

**创建日期:** 2026-01-28
**技能位置:** `C:\Users\oldse\.claude\skills\mysql-docker-client.skill`
