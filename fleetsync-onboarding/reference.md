# FleetSync API 完整参考

> 此文件为 fleetsync-onboarding 技能的参考文档，内容源自 `docs/FleetSync-API-对接文档.md`。
> 技能激活时应加载此文件以获取完整 API 规范。

---

## 基础信息

| 项目 | 说明 |
|------|------|
| 基础 URL | `https://{host}/fleetsync` |
| 协议 | HTTPS |
| 数据格式 | JSON (UTF-8) |
| 认证方式 | Header `X-API-Key: sk-xxxxxxxxxxxxxxxxxxxx` |
| 频率限制 | 100 次/分钟/租户 |
| 坐标系 | WGS84（GPS 原始坐标） |
| 时间格式 | ISO 8601：`2026-02-09T13:00:00` |

---

## 认证

所有 `/api/v1/**` 接口需 Header：`X-API-Key: {apiKey}`

无需认证的端点：
- `/api/public/**`（收件人公开接口）
- `/api/webhooks/**`（供应商回调）

认证失败响应：
- 401, code 2002：API Key 缺失
- 401, code 2003：API Key 无效
- 403, code 2004：租户已禁用

---

## 统一响应格式

```json
{
  "code": 0,
  "message": "success",
  "data": { ... },
  "timestamp": 1707436800000
}
```

---

## 错误码

| 错误码 | HTTP 状态 | 说明 |
|--------|-----------|------|
| 0 | 200 | 成功 |
| 1001 | 400 | 参数错误 |
| 1002 | 400 | 参数校验失败 |
| 2001 | 401 | 未认证 |
| 2002 | 401 | API Key 缺失 |
| 2003 | 401 | API Key 无效 |
| 2004 | 403 | 租户已禁用 |
| 3001 | 404 | 资源不存在 |
| 3003 | 403 | 操作不允许 |
| 3004 | 429 | 请求频率超限 |
| 4001 | 502 | 供应商接口异常 |
| 4002 | 503 | 供应商不可用 |
| 5001 | 500 | 系统内部错误 |

---

## 任务状态流转

```
PENDING → DISPATCHED → ARRIVED_PICKUP → LOADED → IN_TRANSIT → ARRIVED_DELIVERY → COMPLETED
   │
   ├──▶ QUEUED（无空闲车辆时排队）
   └──▶ CANCELLED / FAILED
```

| 状态 | 说明 |
|------|------|
| PENDING | 待处理 |
| QUEUED | 排队等待车辆 |
| DISPATCHED | 已派单，车辆前往取货点 |
| ARRIVED_PICKUP | 车辆到达取货点，可开门装货 |
| LOADED | 已装货，等待出发 |
| IN_TRANSIT | 运输中 |
| ARRIVED_DELIVERY | 到达送货点，可开门取货 |
| COMPLETED | 已完成 |
| CANCELLED | 已取消 |
| FAILED | 失败 |

---

## API 接口详细规范

### 1. 创建报价 `POST /api/v1/quotes`

**请求体：**

```json
{
  "pickupLocation": { "lng": 120.3926, "lat": 36.0671 },
  "deliveryLocation": { "lng": 120.3978, "lat": 36.0695 },
  "vehicleType": "STANDARD"
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| pickupLocation.lng | Double | 是 | 取货点经度（WGS84） |
| pickupLocation.lat | Double | 是 | 取货点纬度（WGS84） |
| deliveryLocation.lng | Double | 是 | 送货点经度 |
| deliveryLocation.lat | Double | 是 | 送货点纬度 |
| vehicleType | String | 否 | 车辆类型 |

**响应 data：**

```json
{
  "quoteNo": "QT202602091234561234",
  "status": "AVAILABLE",
  "statusMessage": "报价有效，可下单",
  "pricing": {
    "basePrice": 20.00,
    "distancePrice": 5.60,
    "totalPrice": 25.60
  },
  "matchedRoute": {
    "pickupStation": { "id": 1, "name": "运营中心站", "distanceMeters": 150 },
    "deliveryStation": { "id": 2, "name": "研发大楼站", "distanceMeters": 200 },
    "routeDistanceKm": 5.60,
    "estimatedMinutes": 15
  },
  "availability": { "vehicleCount": 3, "estimatedWaitMinutes": 5 },
  "expiresAt": "2026-02-09T13:30:00",
  "createdAt": "2026-02-09T13:00:00"
}
```

**报价状态：**

| status | 说明 | 可下单 |
|--------|------|--------|
| AVAILABLE | 有可用路线和车辆 | 是 |
| NO_VEHICLE | 有路线但暂无空闲车辆 | 否（可稍后重试） |
| NO_ROUTE | 无覆盖路线 | 否 |
| EXPIRED | 报价已过期 | 否（需重新报价） |
| USED | 报价已使用 | 否 |

> 报价有效期默认 30 分钟，过期后需重新创建。仅 AVAILABLE 状态可下单。

---

### 2. 查询报价列表 `GET /api/v1/quotes`

**查询参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| status | String | 否 | 状态筛选 |
| createdFrom | DateTime | 否 | 创建时间起（ISO 8601） |
| createdTo | DateTime | 否 | 创建时间止 |
| page | Integer | 否 | 页码（从 0 开始，默认 0） |
| size | Integer | 否 | 每页条数（默认 20） |

**响应 data（分页）：**

```json
{
  "content": [ { ...QuoteResponse... } ],
  "totalElements": 50,
  "totalPages": 3,
  "number": 0,
  "size": 20
}
```

---

### 3. 查询报价详情 `GET /api/v1/quotes/{quoteNo}`

响应 data 同接口 1 的 data 结构。

---

### 4. 检查报价有效性 `GET /api/v1/quotes/{quoteNo}/valid`

**响应 data：** `true`（有效）或 `false`（无效/过期）

---

### 5. 创建任务（下单） `POST /api/v1/tasks`

**请求体：**

```json
{
  "quoteNo": "QT202602091234561234",
  "externalOrderNo": "SDS-2026020900001",
  "pickupContactName": "张三",
  "pickupContactPhone": "13800000001",
  "pickupAddress": "青岛高新区XX路1号",
  "deliveryContactName": "李四",
  "deliveryContactPhone": "13900000001",
  "deliveryAddress": "青岛高新区YY路2号",
  "cargoDescription": "快递包裹",
  "cargoWeight": 5.5,
  "cargoVolume": 0.02,
  "maxWaitMinutes": 10
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| quoteNo | String | 是 | 报价编号（需 AVAILABLE 状态） |
| externalOrderNo | String | 否 | 上游系统订单号（用于关联） |
| pickupContactName | String | 是 | 取货联系人 |
| pickupContactPhone | String | 是 | 取货联系电话 |
| pickupAddress | String | 否 | 取货地址 |
| deliveryContactName | String | 是 | 送货联系人 |
| deliveryContactPhone | String | 是 | 送货联系电话 |
| deliveryAddress | String | 否 | 送货地址 |
| cargoDescription | String | 否 | 货物描述 |
| cargoWeight | Decimal | 否 | 货物重量（kg） |
| cargoVolume | Decimal | 否 | 货物体积（m³） |
| vehicleId | Long | 否 | 指定车辆 ID（不传则自动分配） |
| maxWaitMinutes | Integer | 否 | 无车时最大等待分钟（0=不等待） |

**响应 data：**

```json
{
  "taskNo": "TK202602091234561234",
  "externalOrderNo": "SDS-2026020900001",
  "status": "DISPATCHED",
  "statusMessage": "已派单",
  "vehicle": {
    "id": 1,
    "vehicleCode": "VH-NEO-A1B2C3D4",
    "licensePlate": "鲁B12345",
    "model": "Neolix-01",
    "batteryLevel": 85
  },
  "unlockCode": "A3B7K9",
  "pickupStation": { "id": 1, "name": "运营中心站" },
  "deliveryStation": { "id": 2, "name": "研发大楼站" },
  "pricing": {
    "basePrice": 20.00,
    "distanceFee": 5.60,
    "totalPrice": 25.60
  },
  "estimatedDistanceKm": 5.60,
  "estimatedDurationMinutes": 15,
  "createdAt": "2026-02-09T13:05:00"
}
```

> **unlockCode** 为 6 位字母数字取货码，请妥善保管并转发给取货人。最多尝试 5 次，超过将锁定。

---

### 6. 查询任务列表 `GET /api/v1/tasks`

**查询参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| status | String | 否 | 状态筛选 |
| externalOrderNo | String | 否 | 上游订单号精确匹配 |
| createdFrom | DateTime | 否 | 创建时间起 |
| createdTo | DateTime | 否 | 创建时间止 |
| page | Integer | 否 | 页码（从 0 开始） |
| size | Integer | 否 | 每页条数（默认 20） |

**响应 data（分页）：**

```json
{
  "content": [ { ...TaskResponse... } ],
  "totalElements": 100,
  "totalPages": 5,
  "number": 0,
  "size": 20
}
```

---

### 7. 查询任务详情 `GET /api/v1/tasks/{taskNo}`

响应 data 同接口 5 的 data 结构。

---

### 8. 取消任务 `POST /api/v1/tasks/{taskNo}/cancel`

**约束：** 仅 PENDING / QUEUED / DISPATCHED 状态可取消。

**响应 data：**

```json
{
  "taskNo": "TK202602091234561234",
  "status": "CANCELLED",
  "statusMessage": "已取消"
}
```

---

### 9. 取货开门 `POST /api/v1/tasks/{taskNo}/unlock`

**前提：** 任务状态为 ARRIVED_PICKUP（取货）或 ARRIVED_DELIVERY（送货）。

**请求体：**

```json
{ "unlockCode": "A3B7K9" }
```

**响应 data：**

```json
{
  "taskNo": "TK202602091234561234",
  "status": "ARRIVED_PICKUP",
  "statusMessage": "到达取货点"
}
```

> 取货码最多尝试 5 次，超过后锁定。

---

### 10. 确认装载 `POST /api/v1/tasks/{taskNo}/confirm-loading`

**前提：** 已用取货码开门并放入货物。

**响应 data：**

```json
{
  "taskNo": "TK202602091234561234",
  "status": "LOADED",
  "statusMessage": "已装货"
}
```

---

### 11. 确认签收 `POST /api/v1/tasks/{taskNo}/confirm-delivery`

**前提：** 收件人已从车辆取出货物。

**响应 data：**

```json
{
  "taskNo": "TK202602091234561234",
  "status": "COMPLETED",
  "statusMessage": "已完成"
}
```

---

### 12. 收件人开门（公开接口） `POST /api/public/tasks/{taskNo}/unlock`

**无需 API Key 认证。** 用于短信链接让收件人直接开门。

请求/响应同接口 9。

---

## Webhook 回调

### 配置
Webhook URL 和签名密钥由平台方在租户开通时配置。

### 回调格式

**请求：** `POST {webhookUrl}`

**Headers：**
```
Content-Type: application/json
X-FleetSync-Signature: <HMAC-SHA256 签名>
```

**请求体：**

```json
{
  "eventType": "TASK_STATUS_CHANGE",
  "taskNo": "TK202602091234561234",
  "oldStatus": "DISPATCHED",
  "newStatus": "ARRIVED_PICKUP",
  "remark": "车辆到达取货点",
  "timestamp": 1707436800000
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| eventType | String | 固定 `TASK_STATUS_CHANGE` |
| taskNo | String | 任务编号 |
| oldStatus | String | 变更前状态 |
| newStatus | String | 变更后状态 |
| remark | String | 备注说明 |
| timestamp | Long | 事件时间戳（毫秒） |

### 签名验证

```python
import hmac, hashlib

expected = hmac.new(
    webhook_secret.encode('utf-8'),
    request_body.encode('utf-8'),
    hashlib.sha256
).hexdigest()

assert request.headers['X-FleetSync-Signature'] == expected
```

```java
// Java 示例
import javax.crypto.Mac;
import javax.crypto.spec.SecretKeySpec;

Mac mac = Mac.getInstance("HmacSHA256");
mac.init(new SecretKeySpec(webhookSecret.getBytes("UTF-8"), "HmacSHA256"));
byte[] hash = mac.doFinal(requestBody.getBytes("UTF-8"));
String signature = bytesToHex(hash);
// 比对 request.getHeader("X-FleetSync-Signature") == signature
```

### 重试机制

| 项目 | 说明 |
|------|------|
| 成功条件 | HTTP 2xx |
| 最大重试 | 5 次 |
| 退避策略 | 30s → 60s → 120s → 300s → 600s |
| 超时时间 | 5 秒 |

---

## 对接步骤

1. **获取凭证** — 平台方分配 apiKey、webhookUrl、webhookSecret
2. **报价查询** — `POST /api/v1/quotes`，传入取货/送货 WGS84 坐标
3. **创建订单** — `POST /api/v1/tasks`，使用 AVAILABLE 状态的 quoteNo
4. **跟踪状态** — 轮询 `GET /api/v1/tasks/{taskNo}` 或接收 Webhook
5. **取货** — ARRIVED_PICKUP 后：unlock → 放货 → confirm-loading
6. **签收** — ARRIVED_DELIVERY 后：收件人 unlock → 取货 → confirm-delivery

---

## cURL 示例

**报价查询：**

```bash
curl -X POST https://{host}/fleetsync/api/v1/quotes \
  -H "Content-Type: application/json" \
  -H "X-API-Key: sk-your-api-key" \
  -d '{
    "pickupLocation": {"lng": 120.3926, "lat": 36.0671},
    "deliveryLocation": {"lng": 120.3978, "lat": 36.0695}
  }'
```

**创建任务：**

```bash
curl -X POST https://{host}/fleetsync/api/v1/tasks \
  -H "Content-Type: application/json" \
  -H "X-API-Key: sk-your-api-key" \
  -d '{
    "quoteNo": "QT202602091234561234",
    "externalOrderNo": "YOUR-ORDER-001",
    "pickupContactName": "张三",
    "pickupContactPhone": "13800000001",
    "deliveryContactName": "李四",
    "deliveryContactPhone": "13900000001"
  }'
```

**Webhook 签名验证（Node.js）：**

```javascript
const crypto = require('crypto');

function verifySignature(body, signature, secret) {
  const expected = crypto
    .createHmac('sha256', secret)
    .update(body, 'utf8')
    .digest('hex');
  return expected === signature;
}

// Express 中间件
app.post('/webhook', (req, res) => {
  const body = JSON.stringify(req.body);
  const signature = req.headers['x-fleetsync-signature'];
  if (!verifySignature(body, signature, WEBHOOK_SECRET)) {
    return res.status(401).send('Invalid signature');
  }
  // 处理事件...
  res.status(200).send('OK');
});
```
