---
name: fleetsync-onboarding
description: 指导上游系统完成 FleetSync 无人车调度平台的 API 对接。当用户询问如何对接、需要对接指导、排查对接问题、或生成对接相关代码时使用。
allowed-tools: Read, Grep, Glob, WebFetch, Bash
---

# FleetSync 上游对接指导

基于完整 API 规范指导上游开发者完成 FleetSync 无人车调度平台的 API 对接，包括环境验证、代码生成、问题排查。

## 使用场景

当用户需要以下操作时使用：
- 了解 FleetSync 对接流程或 API 用法
- 生成某语言的 FleetSync SDK 或调用示例代码
- 排查对接过程中遇到的错误（认证失败、报价异常、任务状态不对等）
- 验证 Webhook 签名实现是否正确
- 确认某个接口的请求/响应格式

## 执行流程

1. **加载参考文档**：读取同目录下 `reference.md` 获取完整 API 规范（12 个接口的请求/响应格式、字段定义、状态码等）
2. 如需更详细信息，可补充读取 `docs/FleetSync-API-对接文档.md`
3. 根据用户需求确定对接阶段（见决策规则）
4. 提供精确的技术指导或代码示例
5. 如涉及代码生成，输出可直接运行的完整代码

## 核心知识

### 认证
- Header: `X-API-Key: {apiKey}`
- 所有 `/api/v1/**` 接口需认证
- `/api/public/**` 和 `/api/webhooks/**` 无需认证

### 业务流程（6步）
1. **报价** `POST /api/v1/quotes` → 获得 quoteNo（有效期 10 分钟）
2. **下单** `POST /api/v1/tasks` → 获得 taskNo + unlockCode（6位字母数字取货码）
3. **等待派车** 通过 Webhook 接收 DISPATCHED → ARRIVED_PICKUP
4. **取货** `POST /api/v1/tasks/{taskNo}/unlock` + `confirm-loading`
5. **等待运输** 通过 Webhook 接收 IN_TRANSIT → ARRIVED_DELIVERY
6. **签收** 收件人开门（公开接口无需认证）+ `confirm-delivery`

### API 接口索引（12个）

| # | 方法 | 路径 | 说明 |
|---|------|------|------|
| 1 | POST | `/api/v1/quotes` | 创建报价（传坐标，返回价格/路线/车辆数） |
| 2 | GET | `/api/v1/quotes` | 查询报价列表（分页，可按状态/时间筛选） |
| 3 | GET | `/api/v1/quotes/{quoteNo}` | 查询报价详情 |
| 4 | GET | `/api/v1/quotes/{quoteNo}/valid` | 检查报价有效性 |
| 5 | POST | `/api/v1/tasks` | 创建任务/下单（需 AVAILABLE 报价） |
| 6 | GET | `/api/v1/tasks` | 查询任务列表（分页，可按状态/订单号筛选） |
| 7 | GET | `/api/v1/tasks/{taskNo}` | 查询任务详情 |
| 8 | POST | `/api/v1/tasks/{taskNo}/cancel` | 取消任务（仅 PENDING/QUEUED/DISPATCHED） |
| 9 | POST | `/api/v1/tasks/{taskNo}/unlock` | 取货开门（需取货码，最多 5 次） |
| 10 | POST | `/api/v1/tasks/{taskNo}/confirm-loading` | 确认装载 |
| 11 | POST | `/api/v1/tasks/{taskNo}/confirm-delivery` | 确认签收（任务完成） |
| 12 | POST | `/api/public/tasks/{taskNo}/unlock` | 收件人开门（**无需认证**，短信链接用） |

> 每个接口的完整请求体、响应结构、字段说明见 `reference.md`。

### 任务状态
```
PENDING → DISPATCHED → ARRIVED_PICKUP → LOADED → IN_TRANSIT → ARRIVED_DELIVERY → COMPLETED
```
可取消状态：PENDING / QUEUED / DISPATCHED
其他终态：CANCELLED / FAILED

### Webhook
- 签名算法：HMAC-SHA256(requestBody, webhookSecret)
- 签名 Header：`X-FleetSync-Signature`
- 事件类型：`TASK_STATUS_CHANGE`（含 taskNo, oldStatus, newStatus, remark, timestamp）
- 上游需返回 HTTP 2xx，否则按 30s/60s/120s/300s/600s 退避重试（最多 5 次）

### 统一响应格式
```json
{ "code": 0, "message": "success", "data": { ... }, "timestamp": 1707436800000 }
```
code=0 为成功，其他为错误码。

### 错误码速查
| 码 | 含义 | 上游处理 |
|----|------|---------|
| 0 | 成功 | 正常处理 |
| 1001/1002 | 参数错误/校验失败 | 检查请求参数 |
| 2002/2003 | Key 缺失/无效 | 检查 X-API-Key Header |
| 2004 | 租户已禁用 | 联系平台方 |
| 3001 | 资源不存在 | 检查 quoteNo/taskNo 是否正确 |
| 3003 | 操作不允许 | 检查任务状态是否允许当前操作 |
| 3004 | 频率超限 | 降低请求频率，默认 100次/分 |
| 4001/4002 | 供应商异常/不可用 | 稍后重试 |
| 5001 | 系统内部错误 | 联系平台方 |

### 关键业务规则
- **报价有效期**：10 分钟，仅 AVAILABLE 状态可下单
- **取货码**：6位字母+数字，最多尝试 5 次，超过锁定
- **坐标系**：WGS84（GPS 原始坐标），提醒上游注意坐标转换（高德/百度使用 GCJ-02/BD-09）
- **分页**：page 从 0 开始，默认 size=20

## 决策规则

- 如果用户问「怎么对接」或「对接流程」→ 先加载 reference.md，按6步业务流程逐步说明
- 如果用户问某个接口的详细格式 → 从 reference.md 找到该接口，给出完整请求/响应示例
- 如果用户要生成 SDK/示例代码 → 询问目标语言，生成包含认证、报价、下单、Webhook验签的完整代码
- 如果用户报告错误码 → 根据错误码表给出排查建议
- 如果用户问 Webhook 相关 → 重点说明签名验证算法和重试机制，给出对应语言代码
- 如果用户问「报价返回 NO_VEHICLE」→ 说明是暂无空闲车辆，建议稍后重试或换时间段
- 如果用户问「报价返回 NO_ROUTE」→ 说明取货/送货坐标不在覆盖范围内，检查坐标系是否正确
- 如果用户需要 Postman 集合或测试工具 → 生成 Postman Collection JSON
- 如果用户问「解锁失败」→ 检查取货码是否正确、是否超过 5 次尝试、任务状态是否为 ARRIVED_*

## 约束条件

- **始终先加载 reference.md**，以获取完整的 API 接口规范
- 回答中使用中文（技术术语可用英文）
- 生成的代码必须包含错误处理
- 不泄露内部实现细节（MongoDB、供应商适配器、数据库结构等），只暴露 API 层面信息
- 坐标系始终使用 WGS84，提醒上游注意坐标系转换
