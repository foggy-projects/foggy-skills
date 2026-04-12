# QM 语法手册

<DownloadButton filename="qm-syntax.md" title="下载本文档" />

QM（Query Model，查询模型）用于定义基于 TM 的查询视图，包含可查询的字段和 UI 配置。

## 1. 基本结构

QM 文件使用 JavaScript 语法，导出一个 `queryModel` 对象：

```javascript
export const queryModel = {
    name: 'FactOrderQueryModel',    // 查询模型名称（必填）
    caption: '订单查询',             // 显示名称
    model: 'FactOrderModel',        // 关联的 TM 模型名称（必填）

    columnGroups: [...],            // 列组定义
    orders: [...]                   // 默认排序
};
```

### 1.1 基础字段

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `name` | string | 是 | 查询模型唯一标识 |
| `caption` | string | 否 | 显示名称 |
| `description` | string | 否 | 模型描述（用于 AI 分析上下文） |
| `model` | string/array | 是 | 关联的 TM 模型（单个或多个） |
| `loader` | string | 否 | 加载器版本（`"v2"` 使用 V2 加载器） |
| `columnGroups` | array | 否 | 列组定义 |
| `orders` | array | 否 | 默认排序 |
| `conds` | array | 否 | 预定义查询条件，详见[第10章](#_10-预定义查询条件-conds) |
| `accesses` | array | 否 | 访问控制列表，详见[权限控制](../api/authorization.md) |
| `deprecated` | boolean | 否 | 标记为废弃 |

---

## 2. 单模型关联

最常见的情况是 QM 关联单个 TM：

```javascript
export const queryModel = {
    name: 'FactOrderQueryModel',
    model: 'FactOrderModel',   // 直接使用 TM 名称
    columnGroups: [...]
};
```

---

## 3. 多模型关联

当需要关联多个事实表时，使用 `loadTableModel` 加载模型，通过 `ref` 引用字段。

```javascript
// 加载模型
const fo = loadTableModel('FactOrderModel');
const fp = loadTableModel('FactPaymentModel');

export const queryModel = {
    name: 'OrderPaymentJoinQueryModel',
    caption: '订单支付关联查询',

    // 多模型配置
    model: [
        {
            name: fo,
            alias: 'fo'                    // 表别名
        },
        {
            name: fp,
            alias: 'fp',
            onBuilder: () => {             // JOIN 条件
                return 'fo.order_id = fp.order_id';
            }
        }
    ],

    columnGroups: [
        {
            caption: '订单信息',
            items: [
                { ref: fo.orderId },           // V2：使用 ref 引用
                { ref: fo.orderStatus },
                { ref: fo.customer }           // 维度引用，自动展开为 $id 和 $caption
            ]
        },
        {
            caption: '支付信息',
            items: [
                { ref: fp.paymentId },
                { ref: fp.payAmount }
            ]
        }
    ]
};
```

### 3.1 多模型字段说明

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `name` | string/proxy | 是 | TM 模型名称或 loadTableModel 返回的代理 |
| `alias` | string | 是 | 表别名，用于区分不同模型的字段 |
| `onBuilder` | function | 否 | JOIN 条件构建函数（第二个及之后的模型必填） |

---

## 4. 列组定义 (columnGroups)

列组用于对查询字段进行分组，便于 UI 展示。使用 `loadTableModel` 加载模型后，通过 `ref` 引用字段：

```javascript
const fo = loadTableModel('FactOrderModel');

columnGroups: [
    {
        caption: '订单信息',
        items: [
            { ref: fo.orderId },
            { ref: fo.orderStatus }
        ]
    },
    {
        caption: '客户维度',
        items: [
            { ref: fo.customer },              // 自动展开为 $id + $caption
            { ref: fo.customer$customerType }  // 维度属性
        ]
    }
]
```

**ref 语法优势**：
- IDE 支持代码补全和类型检查
- 重构时自动更新引用
- 编译时即可发现错误

### 4.1 维度引用的自动展开

当 `ref` 指向一个维度（无 `$` 后缀）时，会自动展开为两列：

```javascript
{ ref: fo.customer }
// 等价于自动生成两列：
// customer$id
// customer$caption
```

### 4.2 列组字段

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `caption` | string | 否 | 组名称 |
| `name` | string | 否 | 组标识 |
| `items` | array | 是 | 列项列表 |

### 4.3 列项字段

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `ref` | object | 是 | 字段引用（使用 loadTableModel 代理） |
| `name` | string | 否 | 列名唯一标识（默认使用 ref） |
| `caption` | string | 否 | 覆盖 TM 中的显示名称 |
| `description` | string | 否 | 列描述（用于 AI 分析上下文） |
| `alias` | string | 否 | 输出列别名 |
| `formula` | string | 否 | QM 计算字段公式 |
| `type` | string | 否 | 计算字段返回类型 |
| `partitionBy` | string[] | 否 | 窗口函数 PARTITION BY 列表 |
| `windowOrderBy` | object[] | 否 | 窗口函数 ORDER BY |
| `windowFrame` | string | 否 | 窗口帧定义 |
| `ai` | object | 否 | AI 配置（enabled, prompt, levels） |
| `deprecated` | boolean | 否 | 标记为废弃 |
| `ui` | object | 否 | UI 配置 |

### 4.4 UI 配置

| 字段 | 类型 | 说明 |
|------|------|------|
| `fixed` | string | 固定位置：`left` / `right` |
| `width` | number | 列宽度（像素） |
| `align` | string | 对齐方式：`left` / `center` / `right` |
| `visible` | boolean | 是否默认可见 |

---

## 5. 字段引用格式

使用 `loadTableModel` 加载模型后，通过代理对象引用字段：

```javascript
const fo = loadTableModel('FactOrderModel');

// 事实表属性
fo.orderId
fo.orderStatus

// 度量
fo.totalAmount

// 维度（自动展开为 $id + $caption）
fo.customer

// 维度属性
fo.customer$customerType
fo.customer$province

// 嵌套维度（使用 . 路径语法）
fo.product.category$caption
fo.product.category.group$caption
```

### 5.1 嵌套维度引用

**语法规则**：`.` 负责维度层级导航，`$` 负责属性访问，二者职责分离：

```
fo.product.category$caption
   ├─────────────┘  └──┘
   │  维度路径（.分隔）   属性名（$分隔）
```

**三种引用方式**：

```javascript
// 方式1：完整路径（精确，无需 alias）
{ ref: fo.product.category$caption }
{ ref: fo.product.category.group$caption }

// 方式2：别名（推荐，需在 TM 中定义 alias）
{ ref: fo.productCategory$caption }     // alias: 'productCategory'
{ ref: fo.categoryGroup$caption }       // alias: 'categoryGroup'

// 方式3：DSL 查询中使用下划线格式（输出列名格式）
columns: ["product_category$caption", "product_category_group$caption"]
```

> **注意**：不能用多个 `$` 代替 `.`（如 ~~`product$category$caption`~~），解析器会将第一个 `$` 后的内容整体视为属性名，导致查找失败。

**路径语法说明**：

- `fo.product` → 一级维度
- `fo.product.category` → 二级维度（product 的子维度）
- `fo.product.category$caption` → 二级维度的 caption 属性
- `fo.product.category$id` → 二级维度的 id
- `fo.product.category.group$caption` → 三级维度的 caption

**输出列名格式**：

路径中的 `.` 在输出时自动转为 `_`，避免 JavaScript 属性名冲突：

| QM 引用 | 输出列名 |
|---------|---------|
| `fo.product$caption` | `product$caption` |
| `fo.product.category$caption` | `product_category$caption` |
| `fo.product.category.group$caption` | `product_category_group$caption` |

---

## 6. 默认排序 (orders)

定义查询的默认排序规则：

```javascript
orders: [
    { name: 'orderTime', order: 'desc' },
    { name: 'orderId', order: 'asc' }
]
```

### 6.1 排序字段

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `name` | string | 是 | 排序字段名 |
| `order` | string | 是 | 排序方向：`asc`（升序）/ `desc`（降序） |

---

## 7. 计算字段

可以在 QM 中定义计算字段：

```javascript
columnGroups: [
    {
        caption: '计算字段',
        items: [
            {
                name: 'profitRate',
                caption: '利润率',
                formula: 'profitAmount / salesAmount * 100',
                type: 'NUMBER'
            },
            {
                name: 'avgPrice',
                caption: '平均单价',
                formula: 'totalAmount / totalQuantity',
                type: 'MONEY'
            }
        ]
    }
]
```

### 8.1 计算字段配置

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `name` | string | 是 | 计算字段名 |
| `caption` | string | 否 | 显示名称 |
| `formula` | string | 是 | 计算公式 |
| `type` | string | 否 | 结果数据类型 |

---

## 8. 完整示例

### 8.1 基础查询模型

```javascript
// FactOrderQueryModel.qm

const fo = loadTableModel('FactOrderModel');

export const queryModel = {
    name: 'FactOrderQueryModel',
    caption: '订单查询',
    model: fo,

    columnGroups: [
        {
            caption: '订单信息',
            items: [
                { ref: fo.orderId },
                { ref: fo.orderStatus },
                { ref: fo.orderTime }
            ]
        },
        {
            caption: '客户信息',
            items: [
                { ref: fo.customer },
                { ref: fo.customer$customerType },
                { ref: fo.customer$province }
            ]
        },
        {
            caption: '商品信息',
            items: [
                { ref: fo.product },
                { ref: fo.product$category },
                { ref: fo.product$unitPrice }
            ]
        },
        {
            caption: '度量',
            items: [
                { ref: fo.totalQuantity },
                { ref: fo.totalAmount },
                { ref: fo.profitAmount }
            ]
        }
    ],

    orders: [
        { name: 'orderTime', order: 'desc' }
    ]
};
```

### 8.2 多事实表关联

```javascript
// OrderPaymentQueryModel.qm

const order = loadTableModel('FactOrderModel');
const payment = loadTableModel('FactPaymentModel');

export const queryModel = {
    name: 'OrderPaymentQueryModel',
    caption: '订单支付查询',

    model: [
        {
            name: order,
            alias: 'order'
        },
        {
            name: payment,
            alias: 'payment',
            onBuilder: () => 'order.order_id = payment.order_id'
        }
    ],

    columnGroups: [
        {
            caption: '订单信息',
            items: [
                { ref: order.orderId },
                { ref: order.orderStatus },
                { ref: order.totalAmount }
            ]
        },
        {
            caption: '支付信息',
            items: [
                { ref: payment.paymentId },
                { ref: payment.paymentMethod },
                { ref: payment.paymentAmount },
                { ref: payment.paymentTime }
            ]
        },
        {
            caption: '客户信息',
            items: [
                { ref: order.customer },
                { ref: order.customer$customerType }
            ]
        }
    ],

    orders: [
        { name: 'payment.paymentTime', order: 'desc' }
    ]
};
```

### 8.3 带计算字段的查询模型

```javascript
// SalesAnalysisQueryModel.qm

const fs = loadTableModel('FactSalesModel');

export const queryModel = {
    name: 'SalesAnalysisQueryModel',
    caption: '销售分析',
    model: fs,

    columnGroups: [
        {
            caption: '维度',
            items: [
                { ref: fs.salesDate$year },
                { ref: fs.salesDate$month },
                { ref: fs.product$category },
                { ref: fs.customer$customerType }
            ]
        },
        {
            caption: '基础度量',
            items: [
                { ref: fs.salesQuantity },
                { ref: fs.salesAmount },
                { ref: fs.costAmount },
                { ref: fs.profitAmount }
            ]
        },
        {
            caption: '计算指标',
            items: [
                {
                    name: 'profitRate',
                    caption: '利润率(%)',
                    formula: 'profitAmount / salesAmount * 100',
                    type: 'NUMBER'
                },
                {
                    name: 'avgOrderAmount',
                    caption: '客单价',
                    formula: 'salesAmount / COUNT(*)',
                    type: 'MONEY'
                }
            ]
        }
    ],

    orders: [
        { name: 'salesDate$year', order: 'desc' },
        { name: 'salesDate$month', order: 'desc' }
    ]
};
```

---

## 9. 预定义查询条件 (conds)

预定义查询条件允许在 QM 中声明常用的筛选条件，客户端可直接使用而无需手动构建 slice。

### 9.1 基本结构

```javascript
export const queryModel = {
    name: 'FactOrderQueryModel',
    model: fo,

    conds: [
        {
            name: 'orderStatus',
            field: 'orderStatus',
            type: 'DICT',
            queryType: '='
        },
        {
            name: 'orderDateRange',
            field: 'orderDate$caption',
            type: 'DATE_RANGE',
            queryType: '[)'
        },
        {
            name: 'customerType',
            field: 'customer$customerType',
            type: 'DIM',
            queryType: '='
        },
        {
            name: 'minAmount',
            field: 'totalAmount',
            type: 'DOUBLE',
            queryType: '>='
        }
    ],

    columnGroups: [...]
};
```

### 9.2 条件字段

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `name` | string | 是 | 条件名称 |
| `field` | string | 是 | 对应的查询字段 |
| `column` | string | 否 | 对应的数据库列名 |
| `type` | string | 否 | 条件类型 |
| `queryType` | string | 否 | 默认查询操作符 |

### 9.3 条件类型 (type)

| 类型 | 说明 | 适用场景 |
|------|------|---------|
| `DICT` | 字典类型 | 有字典映射的字段 |
| `DIM` | 维度类型 | 维度属性筛选 |
| `BOOL` | 布尔类型 | 是/否筛选 |
| `DATE_RANGE` | 日期范围 | 日期区间筛选 |
| `DAY_RANGE` | 天数范围 | 天数区间筛选 |
| `COMMON` | 通用类型 | 默认类型 |
| `DOUBLE` | 浮点数 | 数值范围筛选 |
| `INTEGER` | 整数 | 整数值筛选 |

---

## 10. 窗口函数列项

列项支持窗口函数配置，可直接在 QM 中定义窗口计算：

```javascript
columnGroups: [
    {
        caption: '排名分析',
        items: [
            { ref: fo.salesDate },
            { ref: fo.product },
            { ref: fo.salesAmount },
            {
                name: 'salesRank',
                caption: '销售排名',
                formula: 'RANK()',
                partitionBy: ['salesDate$caption'],
                windowOrderBy: [{ field: 'salesAmount', dir: 'desc' }]
            },
            {
                name: 'movingAvg7d',
                caption: '7日移动平均',
                formula: 'AVG(salesAmount)',
                partitionBy: ['product$id'],
                windowOrderBy: [{ field: 'salesDate$caption', dir: 'asc' }],
                windowFrame: 'ROWS BETWEEN 6 PRECEDING AND CURRENT ROW'
            }
        ]
    }
]
```

> 窗口函数在每行数据上独立计算，不触发 GROUP BY。详见 [DSL 查询语法 - 窗口函数](./query-dsl.md#_6-3-支持的表达式)。

---

## 11. 命名约定

### 9.1 文件命名

- QM 文件：`{TM模型名}QueryModel.qm`
- 示例：`FactOrderQueryModel.qm`

### 9.2 模型命名

- 查询模型名：`{TM模型名}QueryModel`
- 示例：`FactOrderQueryModel`

---

## 下一步

- [TM 语法手册](./tm-syntax.md) - 表格模型定义
- [JSON 查询 DSL](./query-dsl.md) - 查询 DSL 完整语法（推荐阅读）
- [父子维度](./parent-child.md) - 层级结构维度
- [计算字段](./calculated-fields.md) - 计算字段详解
- [查询 API](../api/query-api.md) - HTTP API 接口
- [行级权限控制](../api/authorization.md) - 行级数据隔离
