# Spring API 文档生成器技能

为 Spring Controller 接口自动生成符合顺道公司规范的 API 文档。

## 快速开始

### 使用方式

1. **命令调用**
```bash
/spring-api-doc
```

2. **自然语言调用**
```
为 UserController 生成 API 文档
为订单创建接口编写文档
```

### 输入要求

提供以下任一信息：
- Controller 文件路径（如：`src/main/java/com/example/controller/UserController.java`）
- Controller 类名（如：`UserController`）

可选信息：
- 模块名称（默认从包名推断）
- 功能负责人（默认"待填写"）

## 文档结构

### 简单接口（参数≤10，场景<3）

仅生成核心API文档：
```
docs/用户管理/用户管理-登录-POST-API.md (2-4KB)
```

### 复杂接口（参数>10或场景≥3）

生成核心API文档 + 使用手册：
```
docs/订单管理/订单管理-创建-POST-API.md (2-4KB)
docs/订单管理/订单管理-创建-POST-使用手册.md (≤10KB)
```

## 文件命名规范

**重要**：文档会随 Git 提交，检索工具根据 `相对路径+文件名` 直接定位API文档。

### 命名格式

- 简单模块：`{模块名}-{功能名}-{HTTP方法}-API.md`
- 复杂模块：`{一级模块}-{二级模块}-{功能名}-{HTTP方法}-API.md`

### 示例

✓ 正确示例：
- `用户管理-登录-POST-API.md`
- `用户管理-用户详情-GET-API.md`
- `订单管理-创建-POST-API.md`
- `订单管理-售后-创建-POST-API.md`

✗ 错误示例：
- `用户管理-用户-API.md`（缺少HTTP方法）
- `用户管理-查询-GET-API.md`（功能名过于通用）

## 核心特性

### 1. 自动参数解析
- 解析基本类型（String、Integer、Boolean等）
- 读取自定义类定义（DTO、VO等）
- 识别嵌套对象和泛型参数
- 处理枚举类型（`@DictRef` 注解）

### 2. 响应格式识别
- `RX<T>` → `{code, msg, item}` 结构
- `PagingResultImpl<T>` → `{total, items, start, limit}` 结构

### 3. 复杂度评估
- 自动评估接口复杂度
- 简单接口：仅生成核心文档
- 复杂接口：生成核心文档 + 使用手册

### 4. 唯一性保证
- 文件名包含HTTP方法
- 功能名具体明确
- 相对路径+文件名全局唯一

## 文档模板

### 核心API文档

包含：
- 接口信息（路径、方法、认证、负责人）
- 请求参数（表格形式）
- 请求示例（JSON）
- 响应格式（JSON）
- 状态码
- 快速调用（curl 命令）
- 相关文档链接
- 文档标识（用于检索）

### 使用手册（复杂接口）

包含：
- 概述
- 快速开始
- 使用场景（多个场景的完整代码）
- 常见问题（故障排除）
- 相关文档链接
- 文档标识

## 特殊处理

### 枚举类型
- 枚举值 ≤10：列举在参数表中
- 枚举值 >10：添加"使用 sdcode 工具查询"引用

### 嵌套对象
- 使用点号表示嵌套关系
- 示例：`shippingAddress.province`

### 泛型参数
- 识别 `List<T>`、`Map<K,V>` 等泛型
- 提取泛型类型并读取定义

### 分页查询
- 识别 `PagingResultImpl<T>` 返回类型
- 生成标准分页响应结构

## 技能文件

```
spring-api-doc/
├── SKILL.md          # 技能主文件（执行指令）
├── reference.md      # 详细参考文档
├── examples.md       # 文档生成示例
└── README.md         # 本文件
```

## 示例

### 输入

```
为 UserController.login 方法生成文档
```

### 输出

```
✓ 已生成 API 文档：
  - docs/用户管理/用户管理-登录-POST-API.md (2.8KB)

接口信息：
  路径：/api/v1/users/login
  方法：POST
  参数：3 个
  复杂度：简单

文档标识（用于检索）：
  docs/用户管理/用户管理-登录-POST-API.md
```

## 顺道公司特定规范

### RX 响应包装
- 返回结构：`{code, msg, item}`
- **注意**：使用 `item` 字段，非 `data`

### @DictRef 注解
- 标识枚举字典引用
- 需读取枚举类定义

### 文档存放
- 统一存放在 `docs/` 目录
- 按模块划分子目录
- 随代码提交到 Git 仓库

## 维护

- **版本**：1.0.0
- **更新日期**：2026-01-26
- **适用项目**：顺道公司 Spring Boot 项目
