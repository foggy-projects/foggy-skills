# Spring API 文档编写规范 - 参考文档

本文档提供详细的技术规范和扩展信息，供技能执行时查阅。

## 顺道公司规范完整版

### 文档存放路径规范

- 所有API相关文档统一存放于 `docs/` 目录下
- 建议根据模块进行子目录划分
- 推荐结构：
```
docs/
  ├── 用户管理/
  │     ├── 用户管理-登录-API.md
  │     ├── 用户管理-登录-使用手册.md
  │     └── 用户管理-权限验证-API.md
  ├── 订单管理/
  │     ├── 订单管理-创建-API.md
  │     └── 订单管理-创建-使用手册.md
  └── ...
```

### 文档命名规范

**每个接口一个文档** - 一个 Controller 中有 10 个入口，则需要拆成 10 份文档

**重要**：文档会随 Git 提交到代码仓库，检索工具根据 `相对路径+文件名` 直接定位API文档，因此 **必须确保唯一性**。

#### 简单模块
- 格式：`{模块名}-{功能名}-{HTTP方法}-API.md`
- 示例：
  - `用户管理-登录-POST-API.md`
  - `用户管理-用户详情-GET-API.md`
  - `用户管理-更新用户-PUT-API.md`

#### 复杂模块（两级）
- 格式：`{一级模块}-{二级模块}-{功能名}-{HTTP方法}-API.md`
- 示例：
  - `订单管理-售后-创建-POST-API.md`
  - `订单管理-售后-详情-GET-API.md`

#### 使用手册
- 格式：`{模块名}-{功能名}-{HTTP方法}-使用手册.md`
- 示例：
  - `用户管理-登录-POST-使用手册.md`
  - `订单管理-创建-POST-使用手册.md`

#### 唯一性规则
- 必须包含HTTP方法（GET/POST/PUT/DELETE/PATCH）
- 功能名需具体明确，避免过于通用
- 同一目录下不能有重名文件
- 示例对比：
  - ✓ `用户管理-登录-POST-API.md`
  - ✓ `用户管理-用户详情-GET-API.md`
  - ✗ `用户管理-用户-API.md`（缺少HTTP方法，过于通用）
  - ✗ `用户管理-查询-GET-API.md`（功能名过于通用）

### 文档分层策略

#### 核心API文档（必需）
- **文件大小**: 2-4KB（约2000-4000字符）
- **内容**: 接口规范 + 基本示例 + 快速参考
- **适用**: 所有API接口

#### 完整使用手册（按需）
- **文件大小**: 按需，建议不超过10KB
- **内容**: 复杂场景 + 完整代码 + 故障排除 + 相关需求文档引用
- **适用**: 参数>10个或场景>3个的复杂接口

## 功能名生成指南

功能名生成规则，确保文档路径唯一性：

### RESTful 接口模式

| 接口路径 | HTTP方法 | 功能名 | 完整文件名示例 |
|---------|---------|-------|---------------|
| `/users` | GET | 用户列表 | `用户管理-用户列表-GET-API.md` |
| `/users` | POST | 创建用户 | `用户管理-创建用户-POST-API.md` |
| `/users/{id}` | GET | 用户详情 | `用户管理-用户详情-GET-API.md` |
| `/users/{id}` | PUT | 更新用户 | `用户管理-更新用户-PUT-API.md` |
| `/users/{id}` | DELETE | 删除用户 | `用户管理-删除用户-DELETE-API.md` |
| `/users/{id}` | PATCH | 部分更新用户 | `用户管理-部分更新用户-PATCH-API.md` |

### 非 RESTful 接口模式

| 接口路径 | HTTP方法 | 方法名 | 功能名 | 完整文件名示例 |
|---------|---------|-------|-------|---------------|
| `/users/login` | POST | login | 登录 | `用户管理-登录-POST-API.md` |
| `/users/logout` | POST | logout | 登出 | `用户管理-登出-POST-API.md` |
| `/users/changePassword` | POST | changePassword | 修改密码 | `用户管理-修改密码-POST-API.md` |
| `/users/resetPassword` | POST | resetPassword | 重置密码 | `用户管理-重置密码-POST-API.md` |
| `/orders/export` | GET | exportOrders | 导出订单 | `订单管理-导出订单-GET-API.md` |
| `/orders/batchCreate` | POST | batchCreate | 批量创建订单 | `订单管理-批量创建订单-POST-API.md` |

### 功能名冲突处理

当多个接口的功能名可能冲突时，添加路径特征：

```
# 场景：两个用户详情接口
/users/{id}           → 用户管理-普通用户详情-GET-API.md
/admin/users/{id}     → 用户管理-管理员用户详情-GET-API.md

# 场景：不同类型的订单列表
/orders/pending       → 订单管理-待处理订单列表-GET-API.md
/orders/completed     → 订单管理-已完成订单列表-GET-API.md
/orders/cancelled     → 订单管理-已取消订单列表-GET-API.md
```

### 功能名语义化

- 使用动词+名词结构（如：创建订单、查询用户、导出报表）
- 避免过于通用的词汇（如：查询、操作、处理）
- 体现业务含义（如：用户登录 而非 用户认证接口）
- 区分相似功能（如：创建订单 vs 批量创建订单）

## 常用数据结构

### RX<T> - 标准响应包装

**结构**：
```java
public class RX<T> {
    private int code;      // 状态码
    private String msg;    // 消息
    private T item;        // 数据（注意：使用 item，非 data）
}
```

**JSON 示例**：
```json
{
  "code": 200,
  "msg": "成功",
  "item": {
    "id": 1,
    "name": "张三"
  }
}
```

**重要提示**：
- `RX<T>` 使用 `item` 字段，不是 `data`
- 这是顺道公司特定规范
- 文档生成时必须正确识别

### PagingResultImpl<T> - 分页结果

**结构**：
```java
public class PagingResultImpl<T> {
    private long total;     // 总记录数
    private List<T> items;  // 数据列表
    private int start;      // 起始位置
    private int limit;      // 每页大小
}
```

**JSON 示例**：
```json
{
  "total": 100,
  "items": [
    {"id": 1, "name": "张三"},
    {"id": 2, "name": "李四"}
  ],
  "start": 0,
  "limit": 10
}
```

## 参数类型映射

### 基本类型

| Java 类型 | JSON 类型 | 示例 |
|-----------|----------|------|
| String | string | "张三" |
| Integer | number | 123 |
| Long | number | 1234567890 |
| Boolean | boolean | true |
| BigDecimal | number | 99.99 |
| Date | string | "2026-01-26" |

### 复杂类型

#### 自定义类
- 需要读取类定义文件
- 解析所有字段及其注解
- 识别嵌套对象和泛型

#### 集合类型
- `List<T>` → JSON 数组
- `Map<K,V>` → JSON 对象
- `Set<T>` → JSON 数组

#### 枚举类型
- 识别 `@DictRef(XxxType.class)` 注解
- 读取枚举类定义
- 提取枚举值和描述

## Spring 注解识别

### 请求映射注解

```java
@RequestMapping(value = "/api/v1/users", method = RequestMethod.POST)
@PostMapping("/api/v1/users")
@GetMapping("/api/v1/users/{id}")
@PutMapping("/api/v1/users/{id}")
@DeleteMapping("/api/v1/users/{id}")
@PatchMapping("/api/v1/users/{id}")
```

### 参数注解

```java
@RequestBody UserDTO user          // JSON 请求体
@RequestParam String name          // URL 参数 ?name=xxx
@PathVariable Long id              // 路径变量 /users/{id}
@RequestHeader String token        // HTTP 头
```

### 验证注解

```java
@NotNull                           // 必填
@NotBlank                          // 非空字符串
@Size(min=1, max=100)             // 长度限制
@Min(1) @Max(100)                 // 数值范围
@Email                             // 邮箱格式
@Pattern(regexp="...")             // 正则匹配
```

### 字典注解（顺道特有）

```java
@DictRef(OrderStatus.class)        // 枚举字典引用
```

处理方式：
1. 识别 `@DictRef` 注解
2. 提取枚举类名（如 `OrderStatus.class`）
3. 使用 Glob/Grep 搜索枚举类定义
4. 读取枚举值和描述
5. 如果枚举值过多（>10），在文档中添加引用说明

## 复杂度评估标准

### 简单接口（仅需核心API文档）

**判断条件**（满足所有条件）：
- 请求参数 ≤10 个
- 使用场景 <3 个
- 单一业务逻辑
- 无复杂集成需求

**示例**：
```java
@PostMapping("/api/v1/users/login")
public RX<LoginResponse> login(@RequestBody LoginRequest request) {
    // 简单登录逻辑
}
```

### 复杂接口（需要使用手册）

**判断条件**（满足任一条件）：
- 请求参数 >10 个
- 使用场景 ≥3 个
- 涉及多个业务流程
- 需要系统集成说明
- 包含复杂业务规则

**示例**：
```java
@PostMapping("/api/v1/orders/create")
public RX<OrderResponse> createOrder(@RequestBody OrderCreateRequest request) {
    // 复杂订单创建逻辑：库存、价格、优惠、积分、物流等
}
```

## 文档结构对比

### 简单接口文档示例

```
用户管理-登录-API.md (2.8KB)
├── 接口信息（路径、方法、认证）
├── 请求参数（2个参数）
├── 请求示例
├── 响应格式
├── 状态码
└── 快速调用
```

### 复杂接口文档示例

```
订单管理-创建-API.md (3.5KB)
├── 接口信息
├── 请求参数（15个参数，折叠展示）
├── 请求示例
├── 响应格式
├── 状态码
├── 快速调用
└── 相关文档 → 订单管理-创建-使用手册.md

订单管理-创建-使用手册.md (9.2KB)
├── 概述
├── 快速开始
├── 使用场景
│   ├── 场景1：普通订单
│   ├── 场景2：优惠券订单
│   ├── 场景3：积分兑换订单
│   └── 场景4：批量订单
├── 常见问题
└── 相关文档
```

## 文档生成流程详解

### 阶段1：源码分析

1. **读取 Controller 文件**
```java
@RestController
@RequestMapping("/api/v1/users")
public class UserController {

    @PostMapping("/login")
    public RX<LoginResponse> login(@RequestBody LoginRequest request) {
        // ...
    }

    @GetMapping("/{id}")
    public RX<UserDTO> getUser(@PathVariable Long id) {
        // ...
    }
}
```

2. **提取接口信息**
- 类级别路径：`/api/v1/users`
- 方法级别路径：`/login`
- 完整路径：`/api/v1/users/login`
- HTTP 方法：`POST`
- 返回类型：`RX<LoginResponse>`

3. **解析参数**
- `@RequestBody LoginRequest request`
- 需要读取 `LoginRequest` 类定义
- 提取所有字段、类型、注解

### 阶段2：参数解析

1. **定位参数类**
```bash
# 使用 Glob 搜索
pattern: "**/LoginRequest.java"

# 或使用 Grep 搜索
pattern: "class LoginRequest"
```

2. **读取类定义**
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

3. **提取字段信息**
- `username`: String, 必填（@NotBlank）
- `password`: String, 必填（@NotBlank + @Size）
- `rememberMe`: Boolean, 可选

### 阶段3：响应解析

1. **识别返回类型**
```java
RX<LoginResponse>
```

2. **确定响应结构**
- 外层：`RX` → `{code, msg, item}`
- 内层：`LoginResponse` → 需要读取类定义

3. **读取响应类**
```java
public class LoginResponse {
    private String token;
    private Long userId;
    private String username;
    private Date expireTime;
}
```

4. **生成响应示例**
```json
{
  "code": 200,
  "msg": "登录成功",
  "item": {
    "token": "eyJhbGciOiJIUzI1NiIs...",
    "userId": 1001,
    "username": "张三",
    "expireTime": "2026-01-27T10:30:00"
  }
}
```

### 阶段4：文档生成

1. **评估复杂度**
- 参数数量：3 个 ≤10 → 简单
- 场景数量：1 个 <3 → 简单
- 结论：仅生成核心API文档

2. **确定文件路径**
- 模块名：从包名推断 → `用户管理`
- 功能名：从方法名推断 → `登录`
- 文件路径：`docs/用户管理/用户管理-登录-API.md`

3. **生成文档内容**
- 填充模板
- 替换占位符
- 添加实际数据

4. **写入文件**
- 检查目录是否存在
- 创建目录（如需要）
- 写入文档内容

## 特殊场景处理

### 场景1：枚举字典

**源码**：
```java
public class OrderCreateRequest {
    @DictRef(OrderStatus.class)
    private Integer status;
}
```

**处理流程**：
1. 识别 `@DictRef(OrderStatus.class)`
2. 搜索 `OrderStatus.java` 文件
3. 读取枚举定义
4. 如果枚举值 ≤10，列举在参数表中
5. 如果枚举值 >10，添加引用说明

**文档输出**：
```markdown
| 参数 | 类型 | 必填 | 说明 | 示例 |
|------|------|------|------|------|
| status | Integer | 是 | 订单状态（枚举值见 OrderStatus） | 1 |

**OrderStatus 枚举值**：
- 1: 待支付
- 2: 已支付
- 3: 已发货
- 4: 已完成
- 5: 已取消
（更多枚举值请使用 sdcode 工具查询 OrderStatus.class）
```

### 场景2：嵌套对象

**源码**：
```java
public class OrderCreateRequest {
    private String orderNo;
    private List<OrderItem> items;
    private Address shippingAddress;
}

public class OrderItem {
    private Long productId;
    private Integer quantity;
    private BigDecimal price;
}

public class Address {
    private String province;
    private String city;
    private String detail;
}
```

**处理流程**：
1. 识别嵌套对象 `OrderItem` 和 `Address`
2. 递归读取类定义
3. 展开所有字段
4. 使用点号表示嵌套关系

**文档输出**：
```markdown
| 参数 | 类型 | 必填 | 说明 | 示例 |
|------|------|------|------|------|
| orderNo | String | 是 | 订单号 | "ORD20260126001" |
| items | Array | 是 | 订单项列表 | [...] |
| items[].productId | Long | 是 | 商品ID | 1001 |
| items[].quantity | Integer | 是 | 数量 | 2 |
| items[].price | BigDecimal | 是 | 单价 | 99.99 |
| shippingAddress | Object | 是 | 收货地址 | {...} |
| shippingAddress.province | String | 是 | 省份 | "浙江省" |
| shippingAddress.city | String | 是 | 城市 | "杭州市" |
| shippingAddress.detail | String | 是 | 详细地址 | "西湖区xx路xx号" |
```

### 场景3：泛型参数

**源码**：
```java
@PostMapping("/batch")
public RX<List<UserDTO>> batchCreate(@RequestBody List<UserCreateRequest> requests) {
    // ...
}
```

**处理流程**：
1. 识别泛型 `List<UserCreateRequest>`
2. 提取泛型类型 `UserCreateRequest`
3. 读取类定义
4. 在文档中说明数组结构

**文档输出**：
```markdown
## 请求参数

**请求体**：`List<UserCreateRequest>` - 用户创建请求数组

**UserCreateRequest 结构**：

| 参数 | 类型 | 必填 | 说明 | 示例 |
|------|------|------|------|------|
| username | String | 是 | 用户名 | "zhangsan" |
| email | String | 是 | 邮箱 | "zhangsan@example.com" |
| phone | String | 否 | 手机号 | "13800138000" |

## 请求示例
```json
[
  {
    "username": "zhangsan",
    "email": "zhangsan@example.com",
    "phone": "13800138000"
  },
  {
    "username": "lisi",
    "email": "lisi@example.com"
  }
]
```
```

### 场景4：分页查询

**源码**：
```java
@GetMapping("/list")
public RX<PagingResultImpl<UserDTO>> list(
    @RequestParam(defaultValue = "0") int start,
    @RequestParam(defaultValue = "10") int limit,
    @RequestParam(required = false) String keyword
) {
    // ...
}
```

**文档输出**：
```markdown
## 请求参数

| 参数 | 类型 | 必填 | 说明 | 示例 |
|------|------|------|------|------|
| start | int | 否 | 起始位置（默认0） | 0 |
| limit | int | 否 | 每页大小（默认10） | 10 |
| keyword | String | 否 | 搜索关键词 | "张三" |

## 响应格式
```json
{
  "code": 200,
  "msg": "成功",
  "item": {
    "total": 100,
    "items": [
      {
        "id": 1,
        "username": "zhangsan",
        "email": "zhangsan@example.com"
      }
    ],
    "start": 0,
    "limit": 10
  }
}
```

**注意**：返回类型为 `PagingResultImpl<T>` 时，使用标准分页结构
```

## 错误处理

### 参数类找不到
1. 使用 Glob 搜索：`**/{ClassName}.java`
2. 使用 Grep 搜索：`class {ClassName}`
3. 询问用户是否有 sdcode 工具
4. 在文档中标注"需要确认参数结构"

### 枚举类找不到
1. 搜索枚举类定义
2. 如果找不到，在文档中添加：
```markdown
| status | Integer | 是 | 订单状态（枚举值请查询 OrderStatus.class） | 1 |

**注意**：使用 sdcode 工具获取 OrderStatus 枚举定义
```

### 返回类型未知
1. 尝试读取类定义
2. 如果找不到，询问用户
3. 在文档中标注"待确认响应结构"

## Token 优化策略

### 1. 内容精简
- 移除冗余说明
- 合并相似章节
- 使用链接替代重复内容

### 2. 示例简化
- 只保留关键字段
- 省略可选字段
- 使用省略号表示更多内容

### 3. 文档拆分
- 核心内容放在主文档
- 扩展内容放在使用手册
- 通用配置外置到公共文档

## 文档维护

### 更新现有文档
1. 检查文档是否存在
2. 读取现有内容
3. 识别用户自定义部分（场景描述、故障排除）
4. 保留自定义内容
5. 更新接口规范部分
6. 询问用户确认

### 批量生成
1. 识别 Controller 中所有接口方法
2. 逐个生成文档
3. 汇总输出清单
4. 提供批量操作总结

## 质量检查清单

生成文档后检查：
- [ ] 文件路径符合规范
- [ ] 文件大小在合理范围（核心文档 2-4KB）
- [ ] 参数表完整且准确
- [ ] 响应格式正确（RX 使用 item 字段）
- [ ] 快速调用示例可执行
- [ ] 文档间链接正确
- [ ] 枚举类型已展开或添加引用
- [ ] 状态码覆盖常见场景
