# Spring API 文档生成示例

本文档展示实际生成的 API 文档效果。

## 示例1：简单接口 - 用户登录

### 源码

```java
package com.example.controller;

import com.example.dto.LoginRequest;
import com.example.dto.LoginResponse;
import com.example.common.RX;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/v1/users")
public class UserController {

    @PostMapping("/login")
    public RX<LoginResponse> login(@RequestBody LoginRequest request) {
        // 登录逻辑
    }
}
```

**LoginRequest.java**:
```java
public class LoginRequest {
    @NotBlank(message = "用户名不能为空")
    private String username;

    @NotBlank(message = "密码不能为空")
    @Size(min = 6, max = 20, message = "密码长度6-20位")
    private String password;

    private Boolean rememberMe;
}
```

**LoginResponse.java**:
```java
public class LoginResponse {
    private String token;
    private Long userId;
    private String username;
    private Date expireTime;
}
```

### 生成的文档

**文件路径**: `docs/用户管理/用户管理-登录-API.md`

```markdown
# 用户登录 API

## 接口信息
- **路径**: `/api/v1/users/login`
- **方法**: POST
- **认证**: 无
- **负责人**: 待填写

## 请求参数
**重要**：复杂参数需获取源码定义确保准确性

| 参数 | 类型 | 必填 | 说明 | 示例 |
|------|------|------|------|------|
| username | String | 是 | 用户名 | "admin" |
| password | String | 是 | 密码（6-20位） | "123456" |
| rememberMe | Boolean | 否 | 记住我 | true |

## 请求示例
```json
{
  "username": "admin",
  "password": "123456",
  "rememberMe": true
}
```

## 响应格式
```json
{
  "code": 200,
  "msg": "登录成功",
  "item": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "userId": 1001,
    "username": "admin",
    "expireTime": "2026-01-27T10:30:00"
  }
}
```

**注意**：返回类型为 `RX<T>` 时，使用 `item` 字段（非 `data`）

## 状态码
- 200: 登录成功
- 400: 参数错误（用户名或密码为空）
- 401: 认证失败（用户名或密码错误）
- 500: 服务器错误

## 快速调用
```bash
curl -X POST /api/v1/users/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"123456","rememberMe":true}'
```

---
**维护人**: 待填写
**更新日期**: 2026-01-26
```

**复杂度评估**：
- 参数数量：3 个 ≤10 ✓
- 场景数量：1 个 <3 ✓
- 结论：简单接口，仅生成核心API文档

---

## 示例2：复杂接口 - 订单创建

### 源码

```java
package com.example.controller;

import com.example.dto.OrderCreateRequest;
import com.example.dto.OrderResponse;
import com.example.common.RX;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/v1/orders")
public class OrderController {

    @PostMapping("/create")
    public RX<OrderResponse> createOrder(@RequestBody OrderCreateRequest request) {
        // 订单创建逻辑
    }
}
```

**OrderCreateRequest.java**:
```java
public class OrderCreateRequest {
    @NotBlank
    private String orderNo;

    @NotNull
    private Long userId;

    @NotEmpty
    private List<OrderItem> items;

    @NotNull
    private Address shippingAddress;

    private String remark;

    @DictRef(OrderType.class)
    private Integer orderType;

    @DictRef(PaymentMethod.class)
    private Integer paymentMethod;

    private String couponCode;
    private Integer points;
    private BigDecimal shippingFee;
    private String invoiceTitle;
    private String invoiceTaxNo;
}

public class OrderItem {
    private Long productId;
    private Integer quantity;
    private BigDecimal price;
}

public class Address {
    private String province;
    private String city;
    private String district;
    private String detail;
    private String receiverName;
    private String receiverPhone;
}
```

**OrderType.java**:
```java
public enum OrderType {
    NORMAL(1, "普通订单"),
    PRESALE(2, "预售订单"),
    GROUP(3, "团购订单"),
    POINTS(4, "积分兑换"),
    GIFT(5, "赠品订单");

    private final Integer code;
    private final String desc;
}
```

### 生成的文档

#### 核心API文档

**文件路径**: `docs/订单管理/订单管理-创建-API.md`

```markdown
# 订单创建 API

## 接口信息
- **路径**: `/api/v1/orders/create`
- **方法**: POST
- **认证**: Bearer Token
- **负责人**: 待填写

## 请求参数
**重要**：复杂参数需获取源码定义确保准确性

| 参数 | 类型 | 必填 | 说明 | 示例 |
|------|------|------|------|------|
| orderNo | String | 是 | 订单号 | "ORD20260126001" |
| userId | Long | 是 | 用户ID | 1001 |
| items | Array | 是 | 订单项列表 | [...] |
| items[].productId | Long | 是 | 商品ID | 2001 |
| items[].quantity | Integer | 是 | 数量 | 2 |
| items[].price | BigDecimal | 是 | 单价 | 99.99 |
| shippingAddress | Object | 是 | 收货地址 | {...} |
| shippingAddress.province | String | 是 | 省份 | "浙江省" |
| shippingAddress.city | String | 是 | 城市 | "杭州市" |
| shippingAddress.district | String | 是 | 区县 | "西湖区" |
| shippingAddress.detail | String | 是 | 详细地址 | "xx路xx号" |
| shippingAddress.receiverName | String | 是 | 收货人 | "张三" |
| shippingAddress.receiverPhone | String | 是 | 联系电话 | "13800138000" |
| remark | String | 否 | 备注 | "请尽快发货" |
| orderType | Integer | 是 | 订单类型 | 1 |
| paymentMethod | Integer | 是 | 支付方式 | 1 |
| couponCode | String | 否 | 优惠券码 | "COUPON2026" |
| points | Integer | 否 | 使用积分 | 100 |
| shippingFee | BigDecimal | 否 | 运费 | 10.00 |
| invoiceTitle | String | 否 | 发票抬头 | "杭州xx公司" |
| invoiceTaxNo | String | 否 | 税号 | "91330000..." |

**OrderType 枚举值**：
- 1: 普通订单
- 2: 预售订单
- 3: 团购订单
- 4: 积分兑换
- 5: 赠品订单

**PaymentMethod 枚举值**：使用 sdcode 工具查询 PaymentMethod.class

## 请求示例
```json
{
  "orderNo": "ORD20260126001",
  "userId": 1001,
  "items": [
    {
      "productId": 2001,
      "quantity": 2,
      "price": 99.99
    }
  ],
  "shippingAddress": {
    "province": "浙江省",
    "city": "杭州市",
    "district": "西湖区",
    "detail": "文三路xx号",
    "receiverName": "张三",
    "receiverPhone": "13800138000"
  },
  "orderType": 1,
  "paymentMethod": 1,
  "couponCode": "COUPON2026",
  "points": 100
}
```

## 响应格式
```json
{
  "code": 200,
  "msg": "订单创建成功",
  "item": {
    "orderId": 3001,
    "orderNo": "ORD20260126001",
    "totalAmount": 199.98,
    "discountAmount": 10.00,
    "finalAmount": 189.98,
    "status": 1,
    "createTime": "2026-01-26T14:30:00"
  }
}
```

**注意**：返回类型为 `RX<T>` 时，使用 `item` 字段（非 `data`）

## 状态码
- 200: 订单创建成功
- 400: 参数错误（必填字段缺失、格式错误）
- 401: 认证失败（Token无效或过期）
- 403: 权限不足（无创建订单权限）
- 422: 业务错误（库存不足、优惠券无效等）
- 500: 服务器错误

## 快速调用
```bash
curl -X POST /api/v1/orders/create \
  -H "Authorization: Bearer ${token}" \
  -H "Content-Type: application/json" \
  -d '{
    "orderNo": "ORD20260126001",
    "userId": 1001,
    "items": [{"productId": 2001, "quantity": 2, "price": 99.99}],
    "shippingAddress": {
      "province": "浙江省",
      "city": "杭州市",
      "district": "西湖区",
      "detail": "文三路xx号",
      "receiverName": "张三",
      "receiverPhone": "13800138000"
    },
    "orderType": 1,
    "paymentMethod": 1
  }'
```

## 相关文档
- [订单创建使用手册](./订单管理-创建-使用手册.md) - 复杂场景和完整示例

---
**维护人**: 待填写
**更新日期**: 2026-01-26
```

#### 使用手册

**文件路径**: `docs/订单管理/订单管理-创建-使用手册.md`

```markdown
# 订单创建 使用手册

## 概述

订单创建接口支持多种订单类型（普通订单、预售订单、团购订单、积分兑换、赠品订单），并集成了优惠券、积分、发票等功能。

**适用场景**：电商订单创建、商城下单、积分兑换

## 快速开始

```javascript
// 基础订单创建
const result = await fetch('/api/v1/orders/create', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer ${token}',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    orderNo: 'ORD20260126001',
    userId: 1001,
    items: [{
      productId: 2001,
      quantity: 2,
      price: 99.99
    }],
    shippingAddress: {
      province: '浙江省',
      city: '杭州市',
      district: '西湖区',
      detail: '文三路xx号',
      receiverName: '张三',
      receiverPhone: '13800138000'
    },
    orderType: 1,
    paymentMethod: 1
  })
});
```

**前置条件**：
- 权限要求：创建订单权限（`order:create`）
- 依赖服务：商品服务、库存服务、用户服务

## 使用场景

### 场景1：普通订单创建

最基础的订单创建流程，包含商品、收货地址、支付方式。

```javascript
async function createNormalOrder(userId, products, shippingAddress) {
  // 1. 生成订单号
  const orderNo = `ORD${Date.now()}`;

  // 2. 构建订单项
  const items = products.map(p => ({
    productId: p.id,
    quantity: p.quantity,
    price: p.price
  }));

  // 3. 创建订单
  const response = await fetch('/api/v1/orders/create', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${getToken()}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      orderNo,
      userId,
      items,
      shippingAddress,
      orderType: 1, // 普通订单
      paymentMethod: 1 // 支付宝
    })
  });

  const result = await response.json();
  if (result.code === 200) {
    console.log('订单创建成功:', result.item.orderId);
    return result.item;
  }

  throw new Error(result.msg);
}
```

### 场景2：使用优惠券的订单

在普通订单基础上添加优惠券功能。

```javascript
async function createOrderWithCoupon(userId, products, shippingAddress, couponCode) {
  const orderNo = `ORD${Date.now()}`;

  const items = products.map(p => ({
    productId: p.id,
    quantity: p.quantity,
    price: p.price
  }));

  try {
    const response = await fetch('/api/v1/orders/create', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${getToken()}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        orderNo,
        userId,
        items,
        shippingAddress,
        orderType: 1,
        paymentMethod: 1,
        couponCode // 优惠券码
      })
    });

    const result = await response.json();

    if (result.code === 200) {
      console.log('优惠金额:', result.item.discountAmount);
      console.log('实付金额:', result.item.finalAmount);
      return result.item;
    }

    // 优惠券无效的处理
    if (result.code === 422 && result.msg.includes('优惠券')) {
      console.warn('优惠券无效，创建普通订单');
      // 移除优惠券重试
      return createNormalOrder(userId, products, shippingAddress);
    }

    throw new Error(result.msg);
  } catch (error) {
    console.error('订单创建失败:', error);
    throw error;
  }
}
```

### 场景3：积分兑换订单

使用积分抵扣部分金额。

```javascript
async function createPointsOrder(userId, products, shippingAddress, points) {
  const orderNo = `ORD${Date.now()}`;

  const items = products.map(p => ({
    productId: p.id,
    quantity: p.quantity,
    price: p.price
  }));

  // 1. 计算总金额
  const totalAmount = items.reduce((sum, item) => {
    return sum + (item.price * item.quantity);
  }, 0);

  // 2. 验证积分是否充足
  const userPoints = await getUserPoints(userId);
  if (userPoints < points) {
    throw new Error(`积分不足，当前积分：${userPoints}`);
  }

  // 3. 创建订单
  const response = await fetch('/api/v1/orders/create', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${getToken()}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      orderNo,
      userId,
      items,
      shippingAddress,
      orderType: 4, // 积分兑换订单
      paymentMethod: 1,
      points // 使用的积分数
    })
  });

  const result = await response.json();

  if (result.code === 200) {
    console.log('积分抵扣:', points);
    console.log('实付金额:', result.item.finalAmount);
    return result.item;
  }

  throw new Error(result.msg);
}
```

### 场景4：企业订单（含发票）

创建需要开具发票的企业订单。

```javascript
async function createCorporateOrder(orderData) {
  const {
    userId,
    products,
    shippingAddress,
    invoiceInfo // { title, taxNo }
  } = orderData;

  const orderNo = `ORD${Date.now()}`;

  const items = products.map(p => ({
    productId: p.id,
    quantity: p.quantity,
    price: p.price
  }));

  const response = await fetch('/api/v1/orders/create', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${getToken()}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      orderNo,
      userId,
      items,
      shippingAddress,
      orderType: 1,
      paymentMethod: 2, // 对公转账
      invoiceTitle: invoiceInfo.title, // 发票抬头
      invoiceTaxNo: invoiceInfo.taxNo  // 税号
    })
  });

  const result = await response.json();

  if (result.code === 200) {
    console.log('订单创建成功，将开具增值税发票');
    return result.item;
  }

  throw new Error(result.msg);
}
```

### 场景5：批量订单创建

批量创建多个订单（如拆单场景）。

```javascript
async function createBatchOrders(userId, orderGroups, shippingAddress) {
  const results = [];
  const errors = [];

  for (const group of orderGroups) {
    try {
      const orderNo = `ORD${Date.now()}_${group.supplierId}`;

      const response = await fetch('/api/v1/orders/create', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${getToken()}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          orderNo,
          userId,
          items: group.items,
          shippingAddress,
          orderType: 1,
          paymentMethod: 1,
          remark: `供应商：${group.supplierName}`
        })
      });

      const result = await response.json();

      if (result.code === 200) {
        results.push(result.item);
      } else {
        errors.push({
          group: group.supplierName,
          error: result.msg
        });
      }

      // 防止请求过快
      await sleep(100);

    } catch (error) {
      errors.push({
        group: group.supplierName,
        error: error.message
      });
    }
  }

  return {
    success: results,
    failed: errors,
    total: orderGroups.length,
    successCount: results.length,
    failedCount: errors.length
  };
}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}
```

## 常见问题

### 参数错误 (400)

**问题**：必填字段缺失或格式错误

**解决方案**：
- 检查所有必填字段是否已填写
- 验证字段格式（如手机号、金额格式）
- 查看错误消息中的具体提示

**示例**：
```javascript
// 错误：缺少必填字段
{
  "orderNo": "ORD001",
  "userId": 1001
  // 缺少 items 和 shippingAddress
}

// 正确：包含所有必填字段
{
  "orderNo": "ORD001",
  "userId": 1001,
  "items": [...],
  "shippingAddress": {...},
  "orderType": 1,
  "paymentMethod": 1
}
```

### 认证失败 (401)

**问题**：Token 无效或过期

**解决方案**：
- 检查 Token 是否正确设置
- 验证 Token 是否过期
- 重新登录获取新 Token

### 业务错误 (422)

**常见业务错误**：

1. **库存不足**
```json
{
  "code": 422,
  "msg": "商品 [iPhone 15] 库存不足，当前库存：5，需要：10"
}
```
解决：减少购买数量或提示用户

2. **优惠券无效**
```json
{
  "code": 422,
  "msg": "优惠券 [COUPON2026] 已过期"
}
```
解决：移除优惠券或选择其他优惠券

3. **积分不足**
```json
{
  "code": 422,
  "msg": "积分不足，当前积分：50，需要：100"
}
```
解决：减少积分使用数量

### 服务器错误 (500)

**问题**：后端服务异常

**解决方案**：
- 联系技术支持
- 查看服务器日志
- 提供错误发生时的请求数据

## 最佳实践

### 1. 订单号生成

建议使用时间戳 + 用户ID + 随机数：

```javascript
function generateOrderNo(userId) {
  const timestamp = Date.now();
  const random = Math.floor(Math.random() * 1000).toString().padStart(3, '0');
  return `ORD${timestamp}${userId}${random}`;
}
```

### 2. 错误处理

统一错误处理函数：

```javascript
async function handleOrderCreate(orderData) {
  try {
    const result = await createOrder(orderData);
    return { success: true, data: result };
  } catch (error) {
    if (error.code === 422) {
      // 业务错误，展示给用户
      return { success: false, message: error.msg };
    } else {
      // 系统错误，记录日志
      console.error('订单创建失败:', error);
      return { success: false, message: '系统错误，请稍后重试' };
    }
  }
}
```

### 3. 数据验证

前端预验证：

```javascript
function validateOrderData(orderData) {
  const errors = [];

  // 验证必填字段
  if (!orderData.orderNo) errors.push('订单号不能为空');
  if (!orderData.userId) errors.push('用户ID不能为空');
  if (!orderData.items || orderData.items.length === 0) {
    errors.push('订单项不能为空');
  }
  if (!orderData.shippingAddress) errors.push('收货地址不能为空');

  // 验证订单项
  orderData.items?.forEach((item, index) => {
    if (!item.productId) errors.push(`订单项${index + 1}缺少商品ID`);
    if (!item.quantity || item.quantity <= 0) {
      errors.push(`订单项${index + 1}数量无效`);
    }
    if (!item.price || item.price < 0) {
      errors.push(`订单项${index + 1}价格无效`);
    }
  });

  // 验证收货地址
  const addr = orderData.shippingAddress;
  if (addr) {
    if (!addr.province) errors.push('省份不能为空');
    if (!addr.city) errors.push('城市不能为空');
    if (!addr.detail) errors.push('详细地址不能为空');
    if (!addr.receiverName) errors.push('收货人不能为空');
    if (!addr.receiverPhone) errors.push('联系电话不能为空');

    // 验证手机号格式
    if (addr.receiverPhone && !/^1[3-9]\d{9}$/.test(addr.receiverPhone)) {
      errors.push('手机号格式不正确');
    }
  }

  return errors;
}
```

## 相关文档
- [订单创建API文档](./订单管理-创建-API.md) - 接口规范
- [订单状态管理API](./订单管理-状态-API.md) - 订单状态变更
- [订单查询API](./订单管理-查询-API.md) - 订单查询

---
**维护人**: 待填写
**更新日期**: 2026-01-26
```

**复杂度评估**：
- 参数数量：18 个 >10 ✓
- 场景数量：5 个 ≥3 ✓
- 结论：复杂接口，生成核心API文档 + 使用手册

---

## 示例3：分页查询接口

### 源码

```java
@GetMapping("/list")
public RX<PagingResultImpl<UserDTO>> list(
    @RequestParam(defaultValue = "0") int start,
    @RequestParam(defaultValue = "10") int limit,
    @RequestParam(required = false) String keyword,
    @RequestParam(required = false) Integer status
) {
    // 查询逻辑
}
```

### 生成的文档

**文件路径**: `docs/用户管理/用户管理-列表查询-API.md`

```markdown
# 用户列表查询 API

## 接口信息
- **路径**: `/api/v1/users/list`
- **方法**: GET
- **认证**: Bearer Token
- **负责人**: 待填写

## 请求参数

| 参数 | 类型 | 必填 | 说明 | 示例 |
|------|------|------|------|------|
| start | int | 否 | 起始位置（默认0） | 0 |
| limit | int | 否 | 每页大小（默认10） | 10 |
| keyword | String | 否 | 搜索关键词（用户名、手机号） | "张三" |
| status | Integer | 否 | 用户状态（1:正常 2:禁用） | 1 |

## 请求示例

```bash
GET /api/v1/users/list?start=0&limit=10&keyword=张三&status=1
```

## 响应格式

```json
{
  "code": 200,
  "msg": "查询成功",
  "item": {
    "total": 100,
    "items": [
      {
        "id": 1001,
        "username": "zhangsan",
        "phone": "13800138000",
        "email": "zhangsan@example.com",
        "status": 1,
        "createTime": "2026-01-20T10:30:00"
      },
      {
        "id": 1002,
        "username": "zhangsan2",
        "phone": "13800138001",
        "email": "zhangsan2@example.com",
        "status": 1,
        "createTime": "2026-01-21T14:20:00"
      }
    ],
    "start": 0,
    "limit": 10
  }
}
```

**注意**：返回类型为 `PagingResultImpl<T>` 时，使用标准分页结构（total, items, start, limit）

## 状态码
- 200: 查询成功
- 401: 认证失败（Token无效或过期）
- 403: 权限不足（无查询用户列表权限）
- 500: 服务器错误

## 快速调用

```bash
# 基础查询
curl -X GET "/api/v1/users/list?start=0&limit=10" \
  -H "Authorization: Bearer ${token}"

# 关键词搜索
curl -X GET "/api/v1/users/list?keyword=张三&status=1" \
  -H "Authorization: Bearer ${token}"

# 分页查询
curl -X GET "/api/v1/users/list?start=20&limit=20" \
  -H "Authorization: Bearer ${token}"
```

---
**维护人**: 待填写
**更新日期**: 2026-01-26
```

---

## 总结

### 文档生成规则

1. **简单接口**（参数≤10，场景<3）
   - 仅生成核心API文档
   - 文件大小 2-4KB
   - 包含快速参考

2. **复杂接口**（参数>10或场景≥3）
   - 生成核心API文档 + 使用手册
   - 核心文档 2-4KB，使用手册≤10KB
   - 使用手册包含完整场景和故障排除

3. **响应格式处理**
   - `RX<T>` → 使用 `{code, msg, item}` 结构
   - `PagingResultImpl<T>` → 使用 `{total, items, start, limit}` 结构

4. **枚举处理**
   - 枚举值≤10 → 列举在参数表中
   - 枚举值>10 → 添加"使用 sdcode 工具查询"引用
