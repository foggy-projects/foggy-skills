# MySQL Docker Client Skill

通过 Docker 容器执行 MySQL 操作的全局技能，无需本地安装 MySQL。

## 核心特性

✅ **自动容器管理** - 首次使用时自动启动 Docker 容器
✅ **持久化容器** - 容器保持运行，提高后续执行效率
✅ **完整 MySQL 工具集** - 基于官方 MySQL 8.0 镜像
✅ **多种操作** - 查询、DDL、数据导出、SQL 文件执行
✅ **安全设计** - 每次手动提供连接信息，不存储密码

## 技能结构

```
mysql-docker-client/
├── SKILL.md                    # 技能定义（LLM 读取）
├── USAGE.md                    # 使用说明（用户参考）
├── docker/
│   └── docker-compose.yml     # MySQL 客户端容器配置
├── scripts/
│   ├── docker_utils.py        # 容器自动管理工具
│   ├── execute_sql.py         # 执行单条 SQL
│   ├── execute_sql_file.py    # 执行 SQL 文件
│   └── export_data.py         # 导出查询结果
└── references/
    └── mysql-operations.md    # MySQL 操作参考手册
```

## 快速开始

### 1. 安装技能

将 `mysql-docker-client.skill` 文件复制到 Claude 技能目录：
```
C:\Users\oldse\.claude\skills\mysql-docker-client.skill
```

### 2. 使用技能（通过 Claude）

向 Claude 提问时技能会自动触发：

```
User: 查询 MySQL 中 users 表的数据
      数据库: host=192.168.1.100, user=root, password=xxx, database=mydb

Claude: [自动使用 mysql-docker-client 技能]
        1. 自动启动 mysql-client-skill 容器
        2. 执行查询
        3. 返回结果
```

### 3. 直接使用脚本

也可以直接调用脚本：

```bash
# 查询数据
python scripts/execute_sql.py \
  --host 192.168.1.100 \
  --user root \
  --password yourpass \
  --database mydb \
  --sql "SELECT * FROM users LIMIT 10"

# 执行 SQL 文件
python scripts/execute_sql_file.py \
  --host 192.168.1.100 \
  --user root \
  --password yourpass \
  --database mydb \
  --file migration.sql

# 导出数据
python scripts/export_data.py \
  --host 192.168.1.100 \
  --user root \
  --password yourpass \
  --database mydb \
  --sql "SELECT * FROM orders" \
  --output orders.csv \
  --format csv
```

## Docker 容器管理

### 自动管理（推荐）

脚本会自动管理容器：
- 首次运行时自动启动容器
- 容器保持运行供后续使用
- 无需手动操作

### 手动管理（可选）

```bash
# 启动容器
cd docker && docker-compose up -d

# 停止容器
cd docker && docker-compose down

# 查看状态
docker ps | grep mysql-client-skill

# 查看日志
docker logs mysql-client-skill
```

## 支持的操作

| 操作类型 | 说明 | 脚本 |
|---------|------|------|
| 查询数据 | SELECT 查询 | execute_sql.py |
| 修改数据 | INSERT/UPDATE/DELETE | execute_sql.py |
| DDL 操作 | CREATE/ALTER/DROP TABLE | execute_sql.py |
| SQL 文件 | 批量执行 .sql 文件 | execute_sql_file.py |
| 数据导出 | 导出为 CSV/JSON | export_data.py |

## 实际使用示例

### 示例 1: 添加字段

```bash
python scripts/execute_sql.py \
  --host 192.168.31.238 \
  --user root \
  --password "@Shundao888" \
  --database delivery_terminal \
  --sql "ALTER TABLE orders ADD COLUMN status VARCHAR(20)"
```

### 示例 2: 执行迁移脚本

```bash
python scripts/execute_sql_file.py \
  --host 192.168.31.238 \
  --user root \
  --password "@Shundao888" \
  --database delivery_terminal \
  --file sql/alter-add-coupon-fields.sql
```

### 示例 3: 导出数据分析

```bash
python scripts/export_data.py \
  --host 192.168.31.238 \
  --user root \
  --password "@Shundao888" \
  --database delivery_terminal \
  --sql "SELECT * FROM orders WHERE created_at > '2026-01-01'" \
  --output orders_2026.csv
```

## 参考文档

- **SKILL.md** - LLM 读取的技能定义
- **USAGE.md** - 详细使用说明
- **references/mysql-operations.md** - MySQL 操作参考（DDL、索引、迁移模式）

## 技术细节

- **容器名称**: `mysql-client-skill`
- **镜像**: `mysql:8.0`
- **网络模式**: `host` (可访问外部数据库)
- **重启策略**: `unless-stopped`
- **Python 依赖**: 无（仅使用标准库）

## 故障排查

### Docker 未运行
```
Error: Cannot connect to the Docker daemon
→ 启动 Docker Desktop
```

### 网络连接失败
```
Error: Can't connect to MySQL server
→ 检查主机地址、端口和防火墙设置
```

### 权限错误
```
Error: Access denied for user
→ 检查用户名、密码和数据库权限
```

### 容器未启动
```
→ 脚本会自动启动，或手动运行: cd docker && docker-compose up -d
```

## 版本信息

- **创建日期**: 2026-01-28
- **版本**: 1.0.0
- **技能包**: `mysql-docker-client.skill` (13KB)
- **测试状态**: ✅ 已在 Windows 环境测试通过

## 许可

此技能为内部工具，供 Claude Code LLM 使用。
