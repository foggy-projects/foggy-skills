---
name: syntho
description: 顺道私有代码库智能检索助手。当用户需要查找代码、浏览项目、搜索实现、查看源码时使用。支持 /syntho 触发。
allowed-tools: WebFetch
---

# 顺道代码库智能检索助手

顺道公司GitLab私有代码库的一站式检索工具，整合项目浏览、语义搜索、源码查看三大功能。

## 核心能力

| 功能 | 用途 | 典型场景 |
|------|------|----------|
| **浏览** | 查看项目列表、目录结构 | "有哪些项目"、"看看xxx的结构" |
| **搜索** | 语义搜索代码和文档 | "找登录相关代码"、"数据库配置在哪" |
| **源码** | 获取文件完整内容 | "看看UserController的代码" |

## API 端点

**基础URL**: `http://test.synthoflow.com:3003`

> **重要**: 必须使用 **HTTP** 协议，不要使用 HTTPS。这是内网服务，未部署SSL证书。
>
> - 正确: `http://test.synthoflow.com:3003/api/...`
> - 错误: `https://test.synthoflow.com:3003/api/...`

| 接口 | 用途 | 必填参数 |
|------|------|----------|
| `GET /api/projects` | 列出项目 | 无 |
| `GET /api/tree` | 浏览目录 | `path` |
| `GET /api/search` | 语义搜索 | `q` |
| `GET /api/content` | 文件内容 | `path` |

## 执行流程

### 智能任务分解

根据用户需求，自动选择合适的API组合：

**场景1：探索性查询**（不知道代码在哪）
```
1. /api/projects → 了解有哪些项目
2. /api/search?q={关键词} → 语义搜索定位
3. /api/content?path={文件} → 查看具体实现
```

**场景2：定向查询**（知道项目名）
```
1. /api/tree?path=/&project={项目} → 浏览目录结构
2. /api/content?path={文件} → 查看目标文件
```

**场景3：功能查找**（找某个功能的实现）
```
1. /api/search?q={功能描述} → 语义搜索
2. /api/content?path={相关文件} → 查看代码细节
```

**场景4：配置查询**
```
1. /api/tree?path=/config/&project={项目}&pattern=*.yml → 找配置文件
2. /api/content?path={配置文件} → 查看配置内容
```

## 参数速查

### /api/projects
```
?pattern=xxx     # 项目名过滤
&limit=50        # 返回数量
```

### /api/tree
```
?path=/src/      # 目录路径（必填）
&project=xxx     # 项目名（可选，不传则所有项目）
&pattern=*.java  # 文件过滤
&depth=3         # 递归深度，默认2
&format=tree     # tree或json
```

### /api/search
```
?q=用户登录       # 搜索词（必填）
&project=xxx     # 限定项目（可选）
&types=api|java  # 文档类型：all/api/java/general
&limit=10000     # tokens数量
&paths=/api/     # 路径包含，逗号分隔
&exclude=/test/  # 路径排除，逗号分隔
```

### /api/content
```
?path=File.java  # 文件路径（必填）
&start=1         # 起始行
&end=100         # 结束行（与limit互斥）
&limit=2000      # 最大行数
```

## 决策规则

### 选择API的逻辑

```
用户说"有哪些项目/列出项目"
  → /api/projects

用户说"看看xxx项目的结构/目录"
  → /api/tree?path=/&project=xxx

用户说"找xxx相关代码/xxx怎么实现的"
  → /api/search?q=xxx

用户说"看看xxx文件的代码"
  → /api/content?path=xxx
```

### 多步骤任务

```
"syntho-robot项目的登录功能怎么实现的"
  1. 先搜索: /api/search?q=登录功能&project=syntho-robot
  2. 根据结果查看源码: /api/content?path={搜索到的文件}

"找到所有项目的数据库配置"
  1. 列出项目: /api/projects
  2. 对每个项目搜索: /api/search?q=数据库配置&project={项目名}

"不知道在哪个项目，但要找WebSocket相关代码"
  1. 全局搜索: /api/search?q=WebSocket
  2. 定位后查看: /api/content?path={文件}
```

## 常用示例

### 列出所有项目
```
WebFetch: http://test.synthoflow.com:3003/api/projects
prompt: "列出项目名称和描述"
```

### 浏览项目结构
```
WebFetch: http://test.synthoflow.com:3003/api/tree?path=/&project=syntho-robot&depth=2
prompt: "展示目录结构"
```

### 全局搜索代码
```
WebFetch: http://test.synthoflow.com:3003/api/search?q=用户认证
prompt: "展示相关代码片段和文件位置"
```

### 在项目内搜索
```
WebFetch: http://test.synthoflow.com:3003/api/search?q=订单创建&project=syntho-robot&types=java
prompt: "提取订单创建的实现代码"
```

### 查看文件源码
```
WebFetch: http://test.synthoflow.com:3003/api/content?path=UserController.java
prompt: "展示完整源码"
```

### 查看文件特定部分
```
WebFetch: http://test.synthoflow.com:3003/api/content?path=Application.java&start=50&end=100
prompt: "展示第50-100行代码"
```

### 查找配置文件
```
WebFetch: http://test.synthoflow.com:3003/api/tree?path=/&project=syntho-robot&pattern=*.yml&depth=5
prompt: "列出所有yml配置文件"
```

## 输出格式

### 项目列表
```markdown
## 可用项目

| 项目 | 描述 | 文件数 |
|------|------|--------|
| syntho-robot | 机器人核心服务 | 1234 |
| syntho-ai | AI服务模块 | 567 |
```

### 目录结构
```markdown
📁 syntho-robot/
├── 📁 src/
│   ├── 📁 main/java/
│   └── 📁 test/
├── 📄 pom.xml
└── 📄 README.md
```

### 搜索结果
```markdown
## 搜索: {关键词}

### 1. src/controller/UserController.java
**项目**: syntho-robot | **相关度**: 高

\`\`\`java
@PostMapping("/login")
public Result login(@RequestBody LoginRequest req) {
    // 登录逻辑...
}
\`\`\`

### 2. src/service/AuthService.java
...
```

### 源码展示
```markdown
## 📄 UserController.java
**项目**: syntho-robot
**路径**: src/main/java/.../UserController.java

\`\`\`java
package com.syntho.controller;

@RestController
public class UserController {
    ...
}
\`\`\`
```

## 约束条件

- **必须使用 HTTP 协议**，禁止使用 HTTPS（内网服务无SSL）
- 每次WebFetch调用需明确的prompt描述期望输出
- 搜索结果过多时，建议添加 `project` 或 `paths` 参数缩小范围
- 大文件使用 `start/end` 或 `limit` 参数分段读取
- 找不到文件时，先用搜索API定位再查看源码
