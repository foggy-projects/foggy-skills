# FleetSync Mock Server — 集成测试 API 参考

> 此文件为 fleetsync-mock-testing 技能的参考文档。
> Mock Server 端口：**3302**，FleetSync 端口：**12020**

---

## 一、环境搭建

### 前置条件

- Node.js 16+
- Java 17+（运行 FleetSync）
- Maven 3.6+（构建 FleetSync JAR）
- MySQL 8 + MongoDB（需提前启动）

### 一键启动（推荐）

项目根目录提供了一键脚本，**自动完成全部启动流程**：

```bash
# Windows
start.bat

# Linux/Mac
chmod +x start.sh && ./start.sh
```

**脚本自动执行以下 4 步：**

| 步骤 | 操作 | 说明 |
|------|------|------|
| 1/4 | 检查 FleetSync 端口 (12020) | 如有占用则杀掉旧进程 |
| 2/4 | 检查 Mock Server (3302) | 未运行则自动启动 |
| 3/4 | 检查 JAR 是否存在 | 不存在则自动 `mvn package -DskipTests` |
| 4/4 | 启动 FleetSync | profiles: `dev,mock`，连接 Mock Server |

启动后可访问：
- **FleetSync API**: http://localhost:12020/fleetsync
- **Swagger UI**: http://localhost:12020/fleetsync/swagger-ui.html
- **Mock 管理界面**: http://localhost:3302/admin

### 一键停止

```bash
# Windows — 同时停止 FleetSync + Mock Server
stop.bat

# Linux/Mac
./stop.sh
```

### 单独启动 Mock Server

如果只需要 Mock Server（不启动 FleetSync）：

```bash
cd mock-server
npm install        # 首次
start.bat          # Windows
# ./start.sh       # Linux/Mac

# 停止
stop.bat           # Windows
# ./stop.sh        # Linux/Mac
```

### Mock 模式配置说明

FleetSync 使用 `--spring.profiles.active=dev,mock` 启动时：
- `dev` profile: 连接本地 MySQL (3306) + MongoDB (27017)
- `mock` profile: 覆盖供应商 API 地址，指向 Mock Server (3302)

```yaml
# application-mock.yml（自动覆盖供应商配置）
fleetsync:
  suppliers:
    neolix:
      token-base-url: http://localhost:3302
      cloud-api-base-url: http://localhost:3302
      accounts:
        - merchant-code: NEOLIX_QD01
          client-id: 18053159977
          client-secret: f2d8153e-4d4e-4ea4-ac37-bb6a4946ca64
        - merchant-code: NEOLIX_QD02
          client-id: 18053159978
          client-secret: a1b2c3d4-e5f6-7890-abcd-ef1234567890
```

---

## 二、管理 API（测试控制接口）

管理 API 位于 `/admin/api/*`，**无需认证**，用于在测试中控制 Mock Server 的行为。

### 2.1 查询任务列表

**请求：** `GET /admin/api/tasks?merchant={merchantCode}`

**参数：**

| 参数 | 必填 | 说明 |
|------|------|------|
| merchant | 否 | 商户代码，不传则返回所有商户的任务 |

**响应：** JSON 数组

```json
[
  {
    "taskId": "mock-task-1707436800000",
    "vin": "LVSFDFAB1QD000001",
    "merchantCode": "NEOLIX_QD01",
    "startStationId": "1001",
    "endStationId": "1002",
    "status": 2,
    "statusName": "DISPATCHED",
    "remark": "车辆已派出",
    "longitude": 120.3926,
    "latitude": 36.0671,
    "createdAt": "2026-02-10T10:00:00.000Z",
    "updatedAt": "2026-02-10T10:01:00.000Z"
  }
]
```

---

### 2.2 推进任务状态

**请求：** `POST /admin/api/tasks/{taskId}/advance`

**请求体：**

```json
{ "merchantCode": "NEOLIX_QD01" }
```

**行为：** 将任务从当前状态推进到下一个状态（按 1→2→3→4→5→6→7 流程）。推进后自动触发 Webhook 回调到 FleetSync。

**响应：**

```json
{
  "success": true,
  "task": {
    "taskId": "mock-task-1707436800000",
    "status": 3,
    "statusName": "ARRIVED_PICKUP",
    "remark": "已到达取货点",
    "updatedAt": "2026-02-10T10:05:00.000Z"
  },
  "webhookResult": { "success": true, "status": 200 }
}
```

**失败响应：**

```json
{ "success": false, "error": "Task not found" }
{ "success": false, "error": "Cannot advance from status 7" }
```

> 每次调用只前进一步。要从 DISPATCHED(2) 推进到 ARRIVED_PICKUP(3)，调用一次；要到 LOADED(4)，再调用一次。

---

### 2.3 设置任务状态

**请求：** `POST /admin/api/tasks/{taskId}/set-status`

**请求体：**

```json
{
  "merchantCode": "NEOLIX_QD01",
  "status": 6
}
```

**行为：** 直接将任务设置为指定状态（可跳步）。触发 Webhook 回调。状态 ≥ 7 时自动释放车辆。

**响应：** 同 2.2。

**状态码对照：**

| 状态码 | 名称 | 说明 |
|--------|------|------|
| 1 | PENDING | 待执行 |
| 2 | DISPATCHED | 已派车，前往取货点 |
| 3 | ARRIVED_PICKUP | 到达取货点，可开门装货 |
| 4 | LOADED | 已装货，等待出发 |
| 5 | IN_TRANSIT | 运输中 |
| 6 | ARRIVED_DELIVERY | 到达送货点，可开门取货 |
| 7 | COMPLETED | 已完成（释放车辆） |
| 8 | CANCELLED | 已取消（释放车辆） |
| 9 | FAILED | 失败（释放车辆） |

---

### 2.4 配置 Webhook URL

**请求：** `POST /admin/config/webhook`

**请求体（form-urlencoded）：**

```
webhookUrl=http://localhost:12020/fleetsync/api/webhooks/neolix/callback
```

也可通过 JSON body 发送：
```json
{ "webhookUrl": "http://localhost:12020/fleetsync/api/webhooks/neolix/callback" }
```

**说明：** 设置 Mock Server 发送状态变更回调的目标地址。默认已指向本地 FleetSync。

---

## 三、预置测试数据

Mock Server 启动时自动加载以下 seed 数据。所有数据存在内存中，重启即重置。

### 3.1 商户账号

| 商户名 | merchantCode | clientId | clientSecret |
|--------|-------------|----------|--------------|
| 青岛商户A | NEOLIX_QD01 | 18053159977 | f2d8153e-4d4e-4ea4-ac37-bb6a4946ca64 |
| 青岛商户B | NEOLIX_QD02 | 18053159978 | a1b2c3d4-e5f6-7890-abcd-ef1234567890 |

### 3.2 商户A（NEOLIX_QD01）— 青岛高新区

**车辆（3辆）：**

| VIN | 车牌 | 电量 | 位置(lng,lat) | 状态 |
|-----|------|------|--------------|------|
| LVSFDFAB1QD000001 | 鲁B·N001 | 85% | 120.3926, 36.0671 | 空闲 |
| LVSFDFAB1QD000002 | 鲁B·N002 | 92% | 120.3935, 36.0680 | 空闲 |
| LVSFDFAB1QD000003 | 鲁B·N003 | 45% | 120.3918, 36.0665 | 空闲(充电中) |

**站点（5个）：**

| stationId | 名称 | 坐标(lng,lat) |
|-----------|------|--------------|
| 1001 | 高新区运营中心 | 120.3926, 36.0671 |
| 1002 | 研发大楼 | 120.3978, 36.0695 |
| 1003 | 人才公寓 | 120.3890, 36.0650 |
| 1004 | 产业园东门 | 120.3960, 36.0700 |
| 1005 | 地铁高新区站 | 120.3950, 36.0640 |

**路线（3条）：**

| routeId | 名称 | 距离 | 起止站点 | 可用车辆 |
|---------|------|------|---------|---------|
| 100001 | 运营中心→研发大楼 | 1500m | 1001→1002 | 3辆全可用 |
| 100002 | 运营中心→人才公寓 | 800m | 1001→1003 | V001, V002 |
| 100003 | 研发大楼→地铁站 | 1200m | 1002→1005 | V002, V003 |

### 3.3 商户B（NEOLIX_QD02）— 青岛崂山区

**车辆（2辆）：**

| VIN | 车牌 | 电量 | 位置(lng,lat) |
|-----|------|------|--------------|
| LVSFDFAB1QD000101 | 鲁B·N101 | 78% | 120.4680, 36.1100 |
| LVSFDFAB1QD000102 | 鲁B·N102 | 60% | 120.4720, 36.1130 |

**站点（3个）：**

| stationId | 名称 | 坐标(lng,lat) |
|-----------|------|--------------|
| 2001 | 崂山科技城 | 120.4680, 36.1100 |
| 2002 | 青岛国际创新园 | 120.4720, 36.1130 |
| 2003 | 海尔路商圈 | 120.4650, 36.1080 |

**路线（2条）：**

| routeId | 名称 | 距离 | 起止站点 |
|---------|------|------|---------|
| 200001 | 科技城→创新园 | 900m | 2001→2002 |
| 200002 | 科技城→海尔路 | 700m | 2001→2003 |

---

## 四、Webhook 回调

### 4.1 触发时机

任务状态变更时（通过 advance 或 set-status），Mock Server 向 Webhook URL 发送 POST 请求。

### 4.2 回调 payload

```json
{
  "supplierTaskId": "mock-task-1707436800000",
  "statusCode": 3,
  "status": "ARRIVED_PICKUP",
  "longitude": 120.3926,
  "latitude": 36.0671,
  "remark": "已到达取货点",
  "timestamp": 1707436800000
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| supplierTaskId | String | Mock 任务 ID |
| statusCode | Integer | 状态码（1-9） |
| status | String | 状态名称 |
| longitude | Number | 车辆经度 |
| latitude | Number | 车辆纬度 |
| remark | String | 备注 |
| timestamp | Long | 时间戳（毫秒） |

### 4.3 回调链路

```
Mock Server ──webhook──▶ FleetSync ──通知──▶ 上游系统
  (3302)                   (12020)             (webhookUrl)
```

FleetSync 收到 Mock 回调后，更新内部任务状态，再通过 NotificationService 转发给上游系统配置的 webhookUrl。

---

## 五、完整集成测试示例

### 5.1 cURL 手动测试

```bash
FLEETSYNC=http://localhost:12020/fleetsync
MOCK=http://localhost:3302
API_KEY="sk-your-api-key"

# Step 1: 报价
curl -s -X POST $FLEETSYNC/api/v1/quotes \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d '{
    "pickupLocation": {"lng": 120.3926, "lat": 36.0671},
    "deliveryLocation": {"lng": 120.3978, "lat": 36.0695}
  }'
# → 记录 quoteNo

# Step 2: 下单
curl -s -X POST $FLEETSYNC/api/v1/tasks \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d '{
    "quoteNo": "QT...",
    "pickupContactName": "测试发件人",
    "pickupContactPhone": "13800000001",
    "deliveryContactName": "测试收件人",
    "deliveryContactPhone": "13900000001"
  }'
# → 记录 taskNo 和 unlockCode

# Step 3: 查看 Mock 任务（获取 taskId）
curl -s "$MOCK/admin/api/tasks?merchant=NEOLIX_QD01"
# → 找到对应的 taskId

# Step 4: 推进到 ARRIVED_PICKUP
curl -s -X POST "$MOCK/admin/api/tasks/{taskId}/advance" \
  -H "Content-Type: application/json" \
  -d '{"merchantCode": "NEOLIX_QD01"}'
# → Mock 发送 Webhook → FleetSync 更新状态 → 上游收到通知

# Step 5: 解锁车辆
curl -s -X POST "$FLEETSYNC/api/v1/tasks/{taskNo}/unlock" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d '{"unlockCode": "A3B7K9"}'

# Step 6: 确认装载
curl -s -X POST "$FLEETSYNC/api/v1/tasks/{taskNo}/confirm-loading" \
  -H "X-API-Key: $API_KEY"

# Step 7: 推进到 IN_TRANSIT → ARRIVED_DELIVERY
curl -s -X POST "$MOCK/admin/api/tasks/{taskId}/advance" \
  -H "Content-Type: application/json" \
  -d '{"merchantCode": "NEOLIX_QD01"}'
# 重复一次（IN_TRANSIT → ARRIVED_DELIVERY）
curl -s -X POST "$MOCK/admin/api/tasks/{taskId}/advance" \
  -H "Content-Type: application/json" \
  -d '{"merchantCode": "NEOLIX_QD01"}'

# Step 8: 签收
curl -s -X POST "$FLEETSYNC/api/v1/tasks/{taskNo}/confirm-delivery" \
  -H "X-API-Key: $API_KEY"
```

### 5.2 JavaScript (axios) 集成测试

```javascript
const axios = require('axios');

const FLEETSYNC = 'http://localhost:12020/fleetsync';
const MOCK = 'http://localhost:3302';
const API_KEY = 'sk-your-api-key';

const headers = {
  'Content-Type': 'application/json',
  'X-API-Key': API_KEY,
};

async function fullFlowTest() {
  // 1. 报价
  const quoteResp = await axios.post(`${FLEETSYNC}/api/v1/quotes`, {
    pickupLocation: { lng: 120.3926, lat: 36.0671 },
    deliveryLocation: { lng: 120.3978, lat: 36.0695 },
  }, { headers });
  const quoteNo = quoteResp.data.data.quoteNo;
  console.log('Quote:', quoteNo);

  // 2. 下单
  const taskResp = await axios.post(`${FLEETSYNC}/api/v1/tasks`, {
    quoteNo,
    pickupContactName: '测试发件人',
    pickupContactPhone: '13800000001',
    deliveryContactName: '测试收件人',
    deliveryContactPhone: '13900000001',
  }, { headers });
  const { taskNo, unlockCode } = taskResp.data.data;
  console.log('Task:', taskNo, 'UnlockCode:', unlockCode);

  // 3. 获取 Mock taskId
  const mockTasks = await axios.get(`${MOCK}/admin/api/tasks?merchant=NEOLIX_QD01`);
  const mockTask = mockTasks.data.find(t => t.status === 2); // DISPATCHED
  const taskId = mockTask.taskId;
  console.log('Mock TaskId:', taskId);

  // 4. 推进到 ARRIVED_PICKUP
  await axios.post(`${MOCK}/admin/api/tasks/${taskId}/advance`, {
    merchantCode: 'NEOLIX_QD01',
  });
  await sleep(1000); // 等待 Webhook 处理

  // 5. 解锁 + 装载
  await axios.post(`${FLEETSYNC}/api/v1/tasks/${taskNo}/unlock`,
    { unlockCode }, { headers });
  await axios.post(`${FLEETSYNC}/api/v1/tasks/${taskNo}/confirm-loading`,
    {}, { headers });

  // 6. 推进到 ARRIVED_DELIVERY（advance 两次：IN_TRANSIT → ARRIVED_DELIVERY）
  await axios.post(`${MOCK}/admin/api/tasks/${taskId}/advance`, {
    merchantCode: 'NEOLIX_QD01',
  });
  await sleep(500);
  await axios.post(`${MOCK}/admin/api/tasks/${taskId}/advance`, {
    merchantCode: 'NEOLIX_QD01',
  });
  await sleep(1000);

  // 7. 签收
  const result = await axios.post(
    `${FLEETSYNC}/api/v1/tasks/${taskNo}/confirm-delivery`,
    {}, { headers },
  );
  console.log('Completed:', result.data.data.status); // COMPLETED

  console.log('✅ Full flow test passed!');
}

function sleep(ms) {
  return new Promise(r => setTimeout(r, ms));
}

fullFlowTest().catch(console.error);
```

### 5.3 Java (RestTemplate) 集成测试

```java
import org.springframework.web.client.RestTemplate;
import org.springframework.http.*;

public class FleetSyncIntegrationTest {

    static final String FLEETSYNC = "http://localhost:12020/fleetsync";
    static final String MOCK = "http://localhost:3302";
    static final String API_KEY = "sk-your-api-key";

    static RestTemplate rest = new RestTemplate();

    public static void main(String[] args) throws Exception {
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);
        headers.set("X-API-Key", API_KEY);

        // 1. 报价
        String quoteBody = """
            {
              "pickupLocation": {"lng": 120.3926, "lat": 36.0671},
              "deliveryLocation": {"lng": 120.3978, "lat": 36.0695}
            }""";
        ResponseEntity<String> quoteResp = rest.exchange(
            FLEETSYNC + "/api/v1/quotes", HttpMethod.POST,
            new HttpEntity<>(quoteBody, headers), String.class);
        // 解析 quoteNo ...

        // 2. 下单
        String taskBody = String.format("""
            {
              "quoteNo": "%s",
              "pickupContactName": "测试",
              "pickupContactPhone": "13800000001",
              "deliveryContactName": "测试",
              "deliveryContactPhone": "13900000001"
            }""", quoteNo);
        ResponseEntity<String> taskResp = rest.exchange(
            FLEETSYNC + "/api/v1/tasks", HttpMethod.POST,
            new HttpEntity<>(taskBody, headers), String.class);
        // 解析 taskNo, unlockCode ...

        // 3. 推进 Mock 任务
        HttpHeaders mockHeaders = new HttpHeaders();
        mockHeaders.setContentType(MediaType.APPLICATION_JSON);
        rest.exchange(
            MOCK + "/admin/api/tasks/" + mockTaskId + "/advance",
            HttpMethod.POST,
            new HttpEntity<>("{\"merchantCode\":\"NEOLIX_QD01\"}", mockHeaders),
            String.class);
        Thread.sleep(1000);

        // 4. 解锁 → 装载 → 推进 → 签收 ...
    }
}
```

### 5.4 Python (requests) 集成测试

```python
import requests
import time

FLEETSYNC = "http://localhost:12020/fleetsync"
MOCK = "http://localhost:3302"
API_KEY = "sk-your-api-key"

headers = {"Content-Type": "application/json", "X-API-Key": API_KEY}

# 1. 报价
quote = requests.post(f"{FLEETSYNC}/api/v1/quotes", json={
    "pickupLocation": {"lng": 120.3926, "lat": 36.0671},
    "deliveryLocation": {"lng": 120.3978, "lat": 36.0695},
}, headers=headers).json()
quote_no = quote["data"]["quoteNo"]

# 2. 下单
task = requests.post(f"{FLEETSYNC}/api/v1/tasks", json={
    "quoteNo": quote_no,
    "pickupContactName": "测试",
    "pickupContactPhone": "13800000001",
    "deliveryContactName": "测试",
    "deliveryContactPhone": "13900000001",
}, headers=headers).json()
task_no = task["data"]["taskNo"]
unlock_code = task["data"]["unlockCode"]

# 3. 获取 Mock taskId
mock_tasks = requests.get(f"{MOCK}/admin/api/tasks?merchant=NEOLIX_QD01").json()
mock_task_id = next(t["taskId"] for t in mock_tasks if t["status"] == 2)

# 4. 推进到 ARRIVED_PICKUP
requests.post(f"{MOCK}/admin/api/tasks/{mock_task_id}/advance",
              json={"merchantCode": "NEOLIX_QD01"})
time.sleep(1)

# 5. 解锁 + 装载
requests.post(f"{FLEETSYNC}/api/v1/tasks/{task_no}/unlock",
              json={"unlockCode": unlock_code}, headers=headers)
requests.post(f"{FLEETSYNC}/api/v1/tasks/{task_no}/confirm-loading",
              headers=headers)

# 6. 推进到 ARRIVED_DELIVERY（两次 advance）
for _ in range(2):
    requests.post(f"{MOCK}/admin/api/tasks/{mock_task_id}/advance",
                  json={"merchantCode": "NEOLIX_QD01"})
    time.sleep(0.5)
time.sleep(1)

# 7. 签收
result = requests.post(f"{FLEETSYNC}/api/v1/tasks/{task_no}/confirm-delivery",
                       headers=headers).json()
assert result["data"]["status"] == "COMPLETED"
print("✅ Full flow test passed!")
```

---

## 六、调度中心（可视化）

Mock Server 内置调度中心 Web UI，可实时查看车辆位置和任务状态。

| 环境 | 访问地址 |
|------|---------|
| 生产构建 | http://localhost:3302/dispatch/ |
| 开发模式 | http://localhost:5173/dispatch/ |

功能：
- 地图上实时显示车辆位置、站点、路线
- 查看任务状态并手动推进
- 自动推进模式（模拟车辆沿路线行驶）

---

## 七、常见问题排查

### 报价返回 NO_VEHICLE

- 原因：所有车辆 `vehicleAvailable=1`（忙碌）
- 解决：重启 Mock Server 重置数据，或通过管理界面将车辆状态改为空闲

### Webhook 未触发

- 检查 Mock Server 控制台是否有 `[Webhook]` 日志
- 检查 webhook URL 配置：`GET http://localhost:3302/admin/config`
- 确认 FleetSync 已启动且 `/api/webhooks/neolix/callback` 可访问

### 任务推进报 "Task not found"

- 确认 merchantCode 正确（NEOLIX_QD01 或 NEOLIX_QD02）
- 确认 taskId 是 Mock Server 的 ID（非 FleetSync 的 taskNo）
- 通过 `GET /admin/api/tasks?merchant=NEOLIX_QD01` 查看实际 taskId

### 多次测试后车辆全部占用

- 重启 Mock Server 重置所有数据
- 或通过管理界面手动释放车辆（设置 vehicleAvailable=0）
