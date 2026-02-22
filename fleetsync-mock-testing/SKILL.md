---
name: fleetsync-mock-testing
description: 指导上游系统使用 FleetSync Mock Server 完成集成测试。当用户需要搭建测试环境、模拟无人车任务流程、调试 Webhook 回调、或编写集成测试代码时使用。
allowed-tools: Read, Grep, Glob, WebFetch, Bash
---

# FleetSync Mock Server 集成测试指南

指导上游系统开发者使用 FleetSync Mock Server 搭建端到端测试环境，模拟完整的无人车调度流程（报价 → 下单 → 取货 → 运输 → 签收）。

## 使用场景

当用户需要以下操作时使用：
- 搭建 FleetSync + Mock Server 的本地测试环境
- 了解如何通过管理 API 控制任务状态推进
- 编写集成测试代码（模拟完整业务流程）
- 调试 Webhook 回调不触发或回调数据格式问题
- 查看 Mock Server 预置数据（车辆、站点、路线）
- 了解如何重置环境或清理测试数据

## 执行流程

1. **加载参考文档**：读取同目录下 `reference.md` 获取 Mock Server 管理 API 和预置数据的完整规范
2. 根据用户需求确定阶段（见决策规则）
3. 提供精确的技术指导或代码示例
4. 如涉及代码生成，输出可直接运行的完整代码

## 核心知识

### 架构概览

```
上游系统 ──── FleetSync API (:12020) ──── Mock Server (:3302)
   │               │                           │
   │  1. 报价/下单   │  2. 调用供应商API           │  3. 返回模拟数据
   │◀──────────────│──────────────────────────▶│
   │               │                           │
   │  6. Webhook   │  5. 转发到上游              │  4. 管理API推进状态
   │◀──────────────│◀──────────────────────────│◀── 测试代码控制
```

### 一键启动/停止

项目根目录提供了一键脚本，自动启动 Mock Server + FleetSync（mock 模式）：

```bash
# 一键启动（自动检测端口占用、启动 Mock Server、构建 JAR、启动 FleetSync）
start.bat          # Windows
# ./start.sh       # Linux/Mac

# 一键停止（停止 FleetSync + Mock Server）
stop.bat           # Windows
# ./stop.sh        # Linux/Mac
```

也可以单独启动 Mock Server：
```bash
cd mock-server
start.bat          # Windows
# ./start.sh       # Linux/Mac
```

启动后可访问：
- FleetSync API: `http://localhost:12020/fleetsync`
- FleetSync Swagger: `http://localhost:12020/fleetsync/swagger-ui.html`
- Mock Server 管理界面: `http://localhost:3302/admin`

### 启动脚本执行流程

```
[1/4] 检查 FleetSync 端口 (12020)，有占用则杀掉
[2/4] 检查 Mock Server (3302)，未运行则自动启动
[3/4] 检查 JAR 是否存在，不存在则 mvn package
[4/4] 启动 FleetSync (profiles: dev,mock)
```

### 管理 API 索引（用于测试控制）

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/admin/api/tasks?merchant={code}` | 查询任务列表 |
| POST | `/admin/api/tasks/{taskId}/advance` | 推进任务到下一状态 |
| POST | `/admin/api/tasks/{taskId}/set-status` | 设置任务为指定状态 |
| POST | `/admin/config/webhook` | 配置 Webhook 回调 URL |

### 任务状态码

| 状态码 | 名称 | 说明 |
|--------|------|------|
| 1 | PENDING | 待执行 |
| 2 | DISPATCHED | 已派车 |
| 3 | ARRIVED_PICKUP | 到达取货点 |
| 4 | LOADED | 已装货 |
| 5 | IN_TRANSIT | 运输中 |
| 6 | ARRIVED_DELIVERY | 到达送货点 |
| 7 | COMPLETED | 已完成 |
| 8 | CANCELLED | 已取消 |
| 9 | FAILED | 失败 |

正常流程：1 → 2 → 3 → 4 → 5 → 6 → 7

### 典型集成测试流程

```
1. POST /api/v1/quotes          → 获取 quoteNo
2. POST /api/v1/tasks           → 获取 taskNo（Mock 自动创建供应商任务）
3. POST /admin/api/tasks/{id}/advance  → 推进到 ARRIVED_PICKUP (3)
   ↳ FleetSync 收到 Webhook → 转发给上游
4. POST /api/v1/tasks/{taskNo}/unlock  → 解锁
5. POST /api/v1/tasks/{taskNo}/confirm-loading → 确认装载
6. POST /admin/api/tasks/{id}/advance  → 推进到 ARRIVED_DELIVERY (6)
7. POST /api/v1/tasks/{taskNo}/confirm-delivery → 签收完成
```

### 预置测试数据

| 商户 | merchantCode | 车辆 | 站点 | 路线 |
|------|-------------|------|------|------|
| 青岛商户A | NEOLIX_QD01 | 3辆 | 5个 | 3条 |
| 青岛商户B | NEOLIX_QD02 | 2辆 | 3个 | 2条 |

**测试坐标（商户A 青岛高新区，WGS84）：**
- 取货点：`lng=120.3926, lat=36.0671`（运营中心）
- 送货点：`lng=120.3978, lat=36.0695`（研发大楼）

### Webhook 回调

Mock Server 在任务状态变更时向 FleetSync 发送回调，FleetSync 再转发给上游。

回调 payload：
```json
{
  "supplierTaskId": "mock-task-xxx",
  "statusCode": 3,
  "status": "ARRIVED_PICKUP",
  "longitude": 120.3926,
  "latitude": 36.0671,
  "remark": "已到达取货点",
  "timestamp": 1707436800000
}
```

> 完整的管理 API 请求/响应格式、预置数据详情见 `reference.md`

## 决策规则

- 如果用户问「怎么搭建测试环境」→ 按启动步骤说明，提供 start.bat/sh + FleetSync mock profile
- 如果用户问「怎么模拟任务推进」→ 说明 advance API，给出 curl 或代码示例
- 如果用户要生成集成测试代码 → 询问语言，生成包含报价→下单→状态推进→签收的完整测试
- 如果用户问「Webhook 没收到」→ 检查 webhook URL 配置、FleetSync 是否启动
- 如果用户问「任务推进失败」→ 检查 merchantCode 和 taskId 是否正确
- 如果用户问「报价返回 NO_VEHICLE」→ 检查是否有车辆被占用（vehicleAvailable=1），重启 Mock Server 重置
- 如果用户需要测试取消/失败场景 → 使用 set-status API 直接设置状态 8(CANCELLED) 或 9(FAILED)
- 如果用户要测试多商户隔离 → 使用 NEOLIX_QD01 和 NEOLIX_QD02 分别测试

## 约束条件

- **始终先加载 reference.md** 获取完整 API 规范
- Mock Server 数据存储在内存中，重启后重置为 seed 数据
- 回答使用中文（技术术语可用英文）
- 不泄露 FleetSync 内部实现（MongoDB、适配器等），只暴露 API 和 Mock 管理接口
- 坐标系使用 WGS84，提醒上游注意坐标转换
