---
name: spring-api-doc
description: 为 Spring Controller API 编写符合顺道公司规范的文档（两层结构：核心API文档 + 完整使用手册）。当用户需要为 Spring Controller 接口生成API文档、编写接口文档、或使用 /spring-api-doc 时使用。
allowed-tools: Read, Grep, Glob, Bash
---

# Spring API 文档生成器

为 Spring Controller 方法生成符合顺道公司规范的 API 文档（两层结构）。

## 使用场景

当用户需要以下操作时使用：
- 为 Spring Controller 方法生成 API 文档
- 创建符合公司规范的接口文档
- 更新现有 API 文档
- 批量生成多个接口的文档

## 执行流程

### 1. 信息收集阶段

1.1 **定位 Controller 文件**
- 用户提供文件路径 → 直接读取
- 用户提供类名 → 使用 Glob/Grep 搜索
- 用户未提供 → 询问文件路径或类名

1.2 **读取源码**
- 读取完整 Controller 文件
- 识别所有 `@RequestMapping`/`@PostMapping`/`@GetMapping` 等方法
- 提取每个方法的：路径、HTTP方法、参数、返回类型

1.3 **复杂度评估**（每个接口独立评估）
- 参数 ≤10 且场景 <3 → 仅生成核心API文档
- 参数 >10 或场景 ≥3 → 生成核心API文档 + 使用手册

1.4 **检查现有文档目录**
- 检查 `docs/` 目录结构
- 识别已有模块子目录（如 `docs/用户管理/`）
- 避免重复创建目录

### 2. 文档生成阶段

2.1 **确定文件路径（唯一性关键）**
- **重要**：文档会随 Git 提交到代码仓库，检索工具根据 `相对路径+文件名` 直接定位API文档
- 文件命名规则：
  - 无二级模块：`{模块名}-{功能名}-{HTTP方法}-API.md`
  - 有二级模块：`{一级模块}-{二级模块}-{功能名}-{HTTP方法}-API.md`
  - 功能名需体现接口路径特征（如 `/users/{id}` → `获取用户详情`）
- 目录结构：`docs/{模块名}/`
- **唯一性保证**：
  - 同一模块下，不同HTTP方法的同名接口必须在文件名中区分（如 `用户管理-用户-GET-API.md` 与 `用户管理-用户-POST-API.md`）
  - 功能名应避免过于通用（如避免单独使用"查询"、"创建"，应改为"查询用户"、"创建订单"）
  - RESTful 接口应在功能名中体现资源和操作（如 `用户管理-用户详情-GET-API.md`）

2.2 **生成核心API文档**（必需，每个接口一个文件）
- 文件大小：控制在 2-4KB
- 内容结构：见"核心API文档模板"
- 包含快速参考部分

2.3 **生成使用手册**（按需，仅复杂接口）
- 文件命名：`{模块名}-{功能名}-{HTTP方法}-使用手册.md`
- 内容结构：见"使用手册模板"
- 包含完整代码示例和故障排除
- 与核心API文档保持相同的功能名和HTTP方法标识

### 3. 参数解析规则

3.1 **从源码提取参数**
- 解析 `@RequestBody`/`@RequestParam`/`@PathVariable` 注解
- 识别参数类型（基本类型、DTO类、泛型）
- 对于复杂类型（自定义类），需读取类定义文件

3.2 **响应类型处理**
- 识别返回类型：`RX<T>`、`PagingResultImpl<T>`、其他
- `RX<T>` 输出结构：`{code, msg, item}`（非 `data`）
- `PagingResultImpl<T>` 输出结构：`{total, items, start, limit}`

3.3 **字典枚举处理**
- 检测 `@DictRef(XxxType.class)` 注解
- 读取枚举类定义（使用 Glob/Grep 或 sdcode）
- 枚举值较多时，在文档中添加引用说明

### 4. 文档输出阶段

4.1 **写入文件**
- 创建目录（如不存在）
- 写入核心API文档
- 写入使用手册（如需要）

4.2 **建立文档关联**
- 在核心API文档底部添加"相关文档"链接
- 在使用手册中引用核心API文档

## 输入要求

用户需提供：
- **Controller 文件路径或类名**（必需）
- **模块名称**（如未提供则从包名推断）
- **功能负责人**（可选，默认"待填写"）

系统自动获取：
- 接口路径、HTTP方法
- 请求参数、响应格式
- 参数类型定义

## 核心API文档模板

```markdown
# {功能名称} API

## 接口信息
- **路径**: `/api/v1/{path}`
- **方法**: POST/GET/PUT/DELETE
- **认证**: Bearer Token/无
- **负责人**: {负责人姓名}

## 请求参数
**重要**：复杂参数需获取源码定义确保准确性

| 参数 | 类型 | 必填 | 说明 | 示例 |
|------|------|------|------|------|
| {param1} | {type} | 是/否 | {description} | {example} |

## 请求示例
```json
{
  "{param1}": "{value1}",
  "{param2}": "{value2}"
}
```

## 响应格式
```json
{
  "code": 200,
  "msg": "成功",
  "item": {
    "{field1}": "{value1}"
  }
}
```

**注意**：返回类型为 `RX<T>` 时，使用 `item` 字段（非 `data`）

## 状态码
- 200: 成功
- 400: 参数错误
- 401: 认证失败
- 500: 服务器错误

## 快速调用
```bash
curl -X {METHOD} /api/v1/{path} \
  -H "Authorization: Bearer ${token}" \
  -H "Content-Type: application/json" \
  -d '{json_body}'
```

## 相关文档
- [使用手册](./{模块名}-{功能名}-{HTTP方法}-使用手册.md) - 复杂场景（如存在）

---
**文档标识**: docs/{模块名}/{模块名}-{功能名}-{HTTP方法}-API.md
**维护人**: {负责人}
**更新日期**: {YYYY-MM-DD}
```

## 使用手册模板

（仅在接口复杂度评估为"复杂"时生成）

```markdown
# {功能名称} 使用手册

## 概述
简要说明API功能、适用场景和核心价值。

## 快速开始
```javascript
// 基础调用示例
const result = await fetch('/api/v1/{path}', {
  method: '{METHOD}',
  headers: {
    'Authorization': 'Bearer ${token}',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({ param1: 'value1' })
});
```

**前置条件**：
- 权限要求：{permission}
- 依赖服务：{dependencies}

## 使用场景

### 场景1：基础使用
```javascript
async function basicUsage() {
  const response = await fetch('/api/v1/{path}', {
    method: '{METHOD}',
    headers: {
      'Authorization': 'Bearer ${token}',
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      param1: 'value1',
      param2: 'value2'
    })
  });

  const result = await response.json();
  if (result.code === 200) {
    return result.item; // RX<T> 使用 item 字段
  }
  throw new Error(result.msg);
}
```

### 场景2：{高级场景名称}
```javascript
// 完整实现示例
async function advancedUsage() {
  // 场景特定的完整代码
}
```

## 常见问题

### 认证失败 (401)
- 检查 Token 是否过期
- 确认权限配置

### 参数错误 (400)
- 验证必填参数
- 检查参数格式和类型

### 服务器错误 (500)
- 联系技术支持
- 查看错误日志

## 相关文档
- [基础API文档](./{模块名}-{功能名}-{HTTP方法}-API.md) - 接口规范

---
**文档标识**: docs/{模块名}/{模块名}-{功能名}-{HTTP方法}-使用手册.md
**维护人**: {维护人}
**更新日期**: {YYYY-MM-DD}
```

## 约束条件

1. **强制规则**
   - 每个接口必须生成独立的文档文件
   - 核心API文档必须包含快速参考部分
   - 文件大小：核心文档 2-4KB，使用手册 ≤10KB
   - 文件命名必须符合规范（小写、连字符分隔）

2. **响应格式规则**
   - `RX<T>` 返回值 → 使用 `{code, msg, item}` 结构
   - `PagingResultImpl<T>` → 使用 `{total, items, start, limit}` 结构
   - 其他未知类型 → 询问用户或标注"待确认"

3. **参数解析规则**
   - 基本类型（String/Integer/Long/Boolean）→ 直接使用
   - 自定义类 → 必须读取类定义文件
   - 枚举类（@DictRef）→ 读取枚举定义或添加引用说明

4. **目录结构规则**
   - 优先使用现有 `docs/` 子目录
   - 新建目录必须与一级模块名一致
   - 避免创建过深的目录层级（≤2层）

5. **文件命名唯一性规则**
   - 必须包含HTTP方法（GET/POST/PUT/DELETE/PATCH）
   - 功能名需具体明确，避免过于通用
   - 相对路径+文件名组合必须全局唯一
   - 示例：
     - ✓ `docs/用户管理/用户管理-登录-POST-API.md`
     - ✓ `docs/用户管理/用户管理-用户详情-GET-API.md`
     - ✗ `docs/用户管理/用户管理-用户-API.md`（缺少HTTP方法）
     - ✗ `docs/用户管理/用户管理-查询-GET-API.md`（功能名过于通用）

## 决策规则

### 复杂度判断
- 如果 参数 ≤10 且场景 <3 → 仅生成核心API文档
- 如果 参数 >10 或场景 ≥3 → 生成核心API文档 + 使用手册
- 如果 涉及系统集成或复杂业务流程 → 强制生成使用手册

### 参数来源
- 如果 参数类型是基本类型 → 直接从方法签名提取
- 如果 参数类型是自定义类 → 读取类定义文件
- 如果 类定义文件不存在 → 询问用户提供路径或使用 sdcode

### 枚举处理
- 如果 检测到 `@DictRef` → 尝试读取枚举类
- 如果 枚举值 ≤10 个 → 在参数表中列举
- 如果 枚举值 >10 个 → 添加"使用 sdcode 工具获取"引用

### 响应格式
- 如果 返回类型是 `RX<T>` → 使用 `item` 字段（必须）
- 如果 返回类型是 `PagingResultImpl<T>` → 使用标准分页结构
- 如果 返回类型未知 → 询问用户或查找类定义

### 文档关联
- 如果 生成了使用手册 → 在核心API文档添加链接
- 如果 接口属于同一模块 → 在相关文档中互相引用
- 如果 存在需求文档 → 在使用手册中添加需求文档引用

### 功能名生成（唯一性关键）
- 如果 接口路径是 `/users/login` → 功能名：`登录`
- 如果 接口路径是 `/users/{id}` 且 GET → 功能名：`用户详情`
- 如果 接口路径是 `/users/{id}` 且 PUT → 功能名：`更新用户`
- 如果 接口路径是 `/users/{id}` 且 DELETE → 功能名：`删除用户`
- 如果 接口路径是 `/users` 且 GET → 功能名：`用户列表`
- 如果 接口路径是 `/users` 且 POST → 功能名：`创建用户`
- 如果 方法名明确表达功能（如 `exportReport`）→ 使用方法名语义（`导出报表`）
- 如果 功能名冲突 → 添加路径特征（如 `用户管理-管理员用户详情-GET-API.md`）

## 输出格式

完成后输出：
```
✓ 已生成 API 文档：
  - docs/{模块名}/{模块名}-{功能名}-{HTTP方法}-API.md (2.5KB)
  - docs/{模块名}/{模块名}-{功能名}-{HTTP方法}-使用手册.md (8.3KB) [复杂接口]

接口信息：
  路径：{path}
  方法：{method}
  参数：{param_count} 个
  复杂度：{简单/复杂}

文档标识（用于检索）：
  docs/{模块名}/{模块名}-{功能名}-{HTTP方法}-API.md
```

## 特殊处理

### 无法获取参数定义
1. 尝试使用 Glob 搜索类定义
2. 尝试使用 Grep 搜索类名
3. 询问用户是否有 sdcode 工具
4. 最后在文档中标注"需要确认参数结构"

### 多个接口批量生成
1. 识别 Controller 中所有接口方法
2. 逐个生成文档（每个接口独立文件）
3. 汇总输出文档清单

### 文档更新
1. 检查现有文档是否存在
2. 提示用户是否覆盖或合并
3. 保留用户自定义内容（如场景描述、故障排除）
