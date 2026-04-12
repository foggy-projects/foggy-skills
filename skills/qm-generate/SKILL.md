---
name: qm-generate
description: 根据 TM 模型生成 QM（查询模型）文件。当用户要求生成 QM 文件、创建查询模型、或使用 /qm 时使用。
---

# QM Generator

根据 TM 模型生成 QM（查询模型）文件，定义可查询的字段和 UI 配置。

## QM语法规范
如果需要获取更多的qm语法规范，请参考[Foggy QM 语法规范](https://foggy-projects.github.io/foggy-data-mcp-bridge/downloads/qm-syntax.md)

## TM 与 QM 的架构关系

```
TM (表模型)  → 描述数据库表结构，引擎内部自动加载，不可直接查询
QM (查询模型) → 定义用户可查询的视图，是唯一的查询入口
```

**关键设计原则**：
- **TM 不可直接查询**：TM 暴露了表的全部字段（包括 password_hash 等敏感字段），没有访问控制
- **QM 是受控查询视图**：可以选择性暴露字段、添加计算列、未来可加权限过滤
- **TM 不需要注册到 `model-list`**：引擎根据 QM 中的 `loadTableModel()` 调用自动加载所需的 TM
- **只有 QM 需要注册到 `application.yml` 的 `model-list`**

## 使用场景

当用户需要以下操作时使用：
- 根据 TM 模型创建 QM 查询模型文件
- 为事实表生成查询视图
- 创建多模型关联的查询模型
- 添加计算字段到查询模型

## 执行流程

1. 读取 TM 模型文件（使用 Glob 查找 .tm 文件，或使用用户指定的模型路径）
2. 分析 TM 模型结构，提取：
   - 一个或多个模型名称
   - 主模型（root model）与 JOIN 模型
   - 事实表属性字段
   - 维度字段
   - 度量字段
   - 模型之间的关联键（单键或组合键）
3. 生成 QM 文件内容：
   - 使用 `loadTableModel` 加载一个或多个模型
   - 定义 `queryModel` 对象
   - 多模型场景下显式声明 `loader: 'v2'` 和 `joins`
   - 创建 `columnGroups`，按逻辑分组字段
   - **必须包含 TM 的 `idColumn` 对应字段**：如 `fo.orderId`、`fo.staffId`，缺少主键会导致前端 CRUD 操作（编辑/删除/启停）无法调用后端 API
   - 添加默认排序（通常按时间字段降序）
   - **检测 TM 中是否有 `tenant` 维度**：有则生成 `accesses` 块（见"权限控制"章节）
4. 将 QM 文件写入 `{TM模型名}QueryModel.qm`
5. **注册 QM 到 `application.yml`**（见下方"模型注册"章节）
6. 输出文件路径和生成的字段列表

## 输入要求

用户需提供：
- 一个或多个 TM 模型名称或文件路径（必需）
- QM 文件存放路径（可选，默认见下方路径规范）
- 列分组配置（可选，默认按属性、维度、度量分组）
- 多模型场景下的主模型与 JOIN 关系（未提供时需先根据业务语义确认）

## 文件存放路径

**默认路径**（用户未指定时）：
```
src/main/resources/foggy/templates/query/{TM模型名}QueryModel.qm
```

**目录结构说明**：
```
src/main/resources/foggy/templates/
├── model/                    # TM 表模型目录
│   ├── Fact{Name}Model.tm
│   ├── Dim{Name}Model.tm
│   └── mongo/
├── query/                   # QM 查询模型目录
│   ├── {Name}QueryModel.qm  # 查询模型
│   └── mongo/               # MongoDB 查询模型（可选分类）
├── dimensions/              # 维度构建器（可选）
└── dicts.fsscript          # 字典定义
```

如果用户指定了其他路径，按用户指定的路径生成。

## 模型注册

QM 文件生成后，**必须注册到 `application.yml` 的 `model-list`** 才能被查询引擎加载。

### 注册规则

1. **只注册 QM 模型名称**，不需要路径前缀
2. **不要注册 TM 模型**，TM 由引擎根据 `loadTableModel()` 自动加载

### 正确示例

```yaml
mcp:
  semantic:
    model-list:
      - FactScoreQueryModel
      - FactAttendanceQueryModel
      - AggStudentProfileQueryModel
```

### 错误示例

```yaml
# 错误 1: 不要注册 TM 模型
mcp:
  semantic:
    model-list:
      - DimStudentModel          # 错! TM 不需要注册
      - FactScoreModel           # 错! TM 不需要注册
      - FactScoreQueryModel      # 正确

# 错误 2: 不要带路径前缀
mcp:
  semantic:
    model-list:
      - student/query/FactScoreQueryModel   # 错! 不需要路径
      - FactScoreQueryModel                 # 正确
```

## 输出格式

```
QM 文件已生成：{文件路径}

包含字段：
- 事实表属性：{字段列表}
- 维度：{字段列表}
- 度量：{字段列表}
```

## 权限控制（accesses）

QM 通过 `accesses` 块在 **SQL 生成阶段** 注入 WHERE 条件，实现行级数据隔离。

### 生成规则

1. **检测 TM 中是否存在 `tenant` 维度**（`foreignKey: 'tenant_id'`）
   - 有 → 自动生成 `accesses` 块，注入 `tenantId` 过滤
   - 无 → 不生成 `accesses`，输出提示
2. **`@tokenUtils` 依赖**：需宿主服务注册名为 `tokenUtils` 的 Spring Bean，提供 `getToken()` 方法返回 `{ tenantId, ownerOrgId }`
3. **无 token 时必须优雅降级**：用 guard clause 跳过过滤，不能抛异常

### 语法硬约束

| 正确写法 | 错误写法 | 说明 |
|---------|---------|------|
| `queryBuilder: (context) => { const query = context.query; ... }` | `queryBuilder: () => { query.and(...); }` | **必须**从 `context` 参数获取 `query` |
| `query.and(fo.tenantId, token.tenantId)` | `query.and('tenant_id', token.tenantId)` | 推荐使用 `ref` 引用字段 |

### 标准租户隔离模板

```javascript
import { getToken } from '@tokenUtils';
const fo = loadTableModel('XxxModel');

export const queryModel = {
    // ... name, caption, model, columnGroups, orders ...

    accesses: [{
        property: 'tenantId',
        queryBuilder: (context) => {
            const query = context.query;
            const token = getToken();
            if (token && token.tenantId) {
                query.and(fo.tenantId, token.tenantId);
            }
        }
    }]
};
```

### 特殊场景

- **平台端管理页面**（如租户管理列表）：平台管理员可见所有租户，不注入 `tenantId` 过滤，但可注入业务过滤（如 `tenant_flag=1`）
- **多条件过滤**：可在同一个 `queryBuilder` 中追加多个 `query.and()`

## 约束条件（必须严格遵守）

### 硬性语法要求

以下属性名和结构是引擎强制要求的，**不可使用其他变体名**：

| 必须使用 | 禁止使用 | 说明 |
|---------|---------|------|
| `export const queryModel = {...}` | `export const query`, `export const qm` | 导出变量名必须是 `queryModel` |
| `model: fo` | `modelRef: fo`, `tableModel: fo` | TM 引用属性名必须是 `model` |
| `columnGroups: [{ caption, items }]` | `columns: [{ ref, caption }]` | 列定义必须用 `columnGroups` + `items` 结构 |
| `{ ref: fo.fieldName }` | `{ name: 'fieldName' }` | 列引用必须用 `ref` 语法 |
| `loader: 'v2'` + `joins: [...]` | `models: [...]`, `joinGraph: ...` | 多模型 QM 必须通过 `model` + `joins` 描述 |
| `queryBuilder: (context) => { const query = context.query; }` | `queryBuilder: () => { query.and(...); }` | accesses 必须从 context 获取 query |

### 多 TM / JOIN 场景规则

- 一个 QM 可以连接多个 TM；典型写法是先 `loadTableModel()` 多个模型，再指定一个主模型为 `model`
- 多模型场景必须显式声明 `loader: 'v2'`
- `joins` 中每一项都应使用主模型或已接入模型发起连接，如 `fo.leftJoin(fp).on(fo.orderId, fp.orderId)`
- 遇到组合键 JOIN，使用 `.and(...)` 追加关联条件
- `columnGroups.items` 中可以混用多个 TM 的字段引用，如 `{ ref: fo.orderId }`、`{ ref: fp.payAmount }`
- 不要把多个模型塞进数组传给 `model`
- 不要省略 JOIN 条件来源；必须能看出字段属于哪个 TM 别名

### 维度引用前置检查

在 QM 中引用维度字段前，检查 TM 中该维度是否具备完整配置：

- ✅ 有 `tableName`（维度表名）+ `captionColumn`（显示列）→ 可在 QM 中引用，会自动展开 `$id` 和 `$caption`
- ❌ 只有 `foreignKey` 但无 `tableName` → **不可在 QM 中引用该维度**，只能引用 properties 和 measures
- 如果维度配置不完整，在 QM 中跳过该维度并输出警告

### 其他规范

- QM 文件名格式：`{TM模型名}QueryModel.qm`
- 必须使用 `loadTableModel` 加载模型
- 字段引用必须使用 `ref` 语法（V2 语法）
- 维度字段自动展开为 `$id` 和 `$caption` 两列
- 嵌套维度语法：`.` 负责维度层级导航，`$` 负责属性访问，二者不可混用
  - 完整路径：`fo.product.category$caption`、`fo.product.category.group$caption`
  - 别名引用（推荐）：`fo.productCategory$caption`（需 TM 定义 `alias: 'productCategory'`）
  - 禁止写 `product$category$caption`（多个 `$`），解析器无法区分维度路径和属性名
- 输出列名自动转换：路径中 `.` → `_`（如 `product.category$caption` → `product_category$caption`）

## 决策规则

- 如果 TM 模型包含时间字段 → 默认排序使用该字段降序
- 如果用户提供多个 TM 或业务目标明确涉及联合查询 → 优先确认是否需要多模型关联 QM
- 如果 TM 模型包含多个事实表 → 询问用户主表是谁、关联键是什么、是否允许 left join
- 如果用户指定列分组 → 按用户指定的分组生成 columnGroups
- 如果 TM 模型无维度字段 → 仅生成属性和度量分组
- 如果 TM 模型无度量字段 → 仅生成属性和维度分组
- 如果字段名包含中文 → 保留中文字段名，添加 caption 显示名称
- 如果用户需要排名/趋势/利润率等分析字段 → 读取 `references/predefined-calculated-fields.md` 生成预定义计算字段
- 如果是多模型场景 → 默认选择业务主实体对应的 TM 作为 `model`，其余 TM 通过 `joins` 接入
- 如果主模型和从模型粒度不同 → 明确提示用户确认聚合风险和字段暴露范围

## 默认列分组策略

1. **基础信息组**：包含所有事实表属性（非维度、非度量字段）
2. **维度组**：包含所有维度字段，使用 `ref` 引用自动展开
3. **度量组**：包含所有度量字段

## 单 TM 示例输出

```javascript
import { getToken } from '@tokenUtils';

const fo = loadTableModel('FactOrderModel');

export const queryModel = {
    name: 'FactOrderQueryModel',
    caption: '订单查询',
    model: fo,

    columnGroups: [
        {
            caption: '基础信息',
            items: [
                { ref: fo.orderId },
                { ref: fo.orderStatus },
                { ref: fo.orderTime }
            ]
        },
        {
            caption: '维度',
            items: [
                { ref: fo.customer },
                { ref: fo.product },
                { ref: fo.region }
            ]
        },
        {
            caption: '度量',
            items: [
                { ref: fo.totalQuantity },
                { ref: fo.totalAmount }
            ]
        }
    ],

    orders: [
        { name: 'orderTime', order: 'desc' }
    ],

    accesses: [{
        property: 'tenantId',
        queryBuilder: (context) => {
            const query = context.query;
            const token = getToken();
            if (token && token.tenantId) {
                query.and(fo.tenantId, token.tenantId);
            }
        }
    }]
};
```

## 多 TM JOIN 示例

`foggy-dataset-demo` 中已经有多 TM QM 示例，例如：

- `OrderPaymentJoinQueryModel.qm`：`FactOrderModel + FactPaymentModel`
- `SalesReturnJoinQueryModel.qm`：`FactSalesModel + FactReturnModel`

生成多 TM QM 时，优先参考这种结构：

```javascript
const fo = loadTableModel('FactOrderModel');
const fp = loadTableModel('FactPaymentModel');

export const queryModel = {
    name: 'OrderPaymentJoinQueryModel',
    caption: '订单支付联合查询',
    description: '多事实表JOIN场景 - 订单表与支付表联合查询',
    loader: 'v2',
    model: fo,

    joins: [
        fo.leftJoin(fp).on(fo.orderId, fp.orderId)
    ],

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
            caption: '支付信息',
            items: [
                { ref: fp.paymentId },
                { ref: fp.payMethod },
                { ref: fp.payAmount }
            ]
        }
    ]
};
```

组合键 JOIN 示例：

```javascript
const fs = loadTableModel('FactSalesModel');
const fr = loadTableModel('FactReturnModel');

export const queryModel = {
    name: 'SalesReturnJoinQueryModel',
    caption: '销售退货联合查询',
    loader: 'v2',
    model: fs,
    joins: [
        fs.leftJoin(fr).on(fs.orderId, fr.orderId).and(fs.orderLineNo, fr.orderLineNo)
    ],
    columnGroups: [
        {
            caption: '销售与退货',
            items: [
                { ref: fs.orderId },
                { ref: fs.orderLineNo },
                { ref: fr.returnId },
                { ref: fr.returnAmount }
            ]
        }
    ]
};
```
