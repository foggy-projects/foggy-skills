---
name: foggy-model-chain-iteration
description: Foggy 模型链路迭代向导。用于围绕 DDL/TM/QM/API/前端组件这一条开发链路分析当前状态、确定下一步工作、编排技能调用顺序。当用户开始模型驱动开发迭代、询问这条链路下一步该做什么、或使用 /iterate 时使用。不要把它当作通用项目治理、版本规划、子模块落盘或验收 skill。
---

# Foggy 模型链路迭代向导

分析 Foggy 项目中与模型驱动开发相关的当前状态，自动确定所处阶段，编排下一步工作并引导执行。

## 使用场景

当用户需要以下操作时使用：
- 开始新一轮模型驱动开发迭代
- 询问 TM/QM/API/前端组件链路下一步该做什么
- 检查 DDL、TM、QM、后端接口、前端组件之间缺了哪一环
- 新会话中恢复这条开发链路的上下文

不适用：
- 规划根目录与子目录协作边界
- 评估需求或方案是否合理
- 生成 root 总控执行文档
- 将版本文档 fan-out 到各子模块
- 做版本级或功能级验收签收

这些场景分别优先使用：
- `workspace-governance-handbook`
- `plan-evaluator`
- `foggy-plan-execution-docs`
- `foggy-versioned-doc-tracking`
- `foggy-acceptance-signoff`

## 执行流程

### 1. 链路状态扫描

依次执行以下检查，建立模型链路全貌：

**基础信息**：
- 读取 `CLAUDE.md` 获取项目配置（模型路径、前端路径、接口约定等）
- 读取 `pom.xml` 或 `package.json` 确认依赖版本
- 判断是否已经完成 `foggy-data-viewer` 或相关前端初始化

**数据模型层**：
- 检查 `sql/` 目录是否有 DDL 文件
- 扫描 TM 模型目录（从 CLAUDE.md 获取路径），统计已有 TM 文件数量
- 扫描 QM 模型目录，统计已有 QM 文件数量
- 读取配置文件检查 `model-list` 或等效模型注册配置
- 如有验证链路，检查是否有 QM 校验记录或可运行命令

**接口封装层**：
- 扫描 Controller 类数量和 API 端点
- 扫描 Service 类数量
- 扫描 DTO/Form 类数量
- 检查是否已有 DSL 查询封装或业务查询 API

**前端代码层**：
- 检查 `frontend/` 目录是否存在
- 扫描 Vue 组件数量
- 检查是否有 foggy-data-viewer 配置
- 检查路由配置
- 检查是否已有 generated 组件和页面包装层

**进度记录**：
- 读取 `docs/notes/` 下最近的进度笔记，了解上次迭代状态
- 如存在模块级开发记录，读取最近一条作为补充上下文

### 2. 判断链路阶段

根据扫描结果，判断项目处于以下哪个阶段：

| 阶段 | 判定条件 | 下一步动作 |
|---|---|---|
| **S0 - 链路准备** | 无 CLAUDE.md 或缺少关键模型/前端目录配置 | 补齐链路基础配置 |
| **S1 - 数据模型设计** | 有项目结构，无 DDL 文件 | 引导设计数据模型 |
| **S2 - TM 模型生成** | 有 DDL，TM 文件数 < DDL 表数 | 调用 `/tm-generate` 或 `/tm-generate-mongo` |
| **S3 - QM 模型生成** | TM 完整，无 QM 文件 | 调用 `/qm-generate` |
| **S4 - 模型校验** | QM 已生成，但未验证 | 调用 `/qm-validate` |
| **S5 - 后端查询/API 开发** | QM 可用，但接口或查询封装不足 | 调用 `/backend-dsl-query`、`/form-design` |
| **S6 - 前端接入与组件开发** | 后端能力已具备，前端组件不足 | 调用 `/foggy-frontend-init`、`/frontend-component-generator`、`/frontend-dsl-query` |
| **S7 - 测试与迭代增强** | 基础链路完整，需要测试或增量完善 | 调用 `/integration-test` 或分析增量需求 |

### 3. 输出迭代计划

格式：

```
## 链路状态：{阶段名称}

### 已完成
- {已完成项1}
- {已完成项2}

### 当前阶段：{阶段描述}

建议执行以下步骤：

1. **{步骤1}** → 使用 `/{技能名}`
2. **{步骤2}** → 使用 `/{技能名}`
3. **{步骤3}** → 手动操作

### 依赖检查
- [ ] {前置条件1}（状态：pass/fail）
- [ ] {前置条件2}（状态：pass/fail）
```

### 4. 引导执行

- 按步骤顺序引导用户执行
- 每步完成后自动检查结果
- 遇到阻塞时提示解决方案
- 链路完成后建议生成进度笔记（`/xiaohongshu-note`）

## 技能调用链

标准模型链路迭代的技能调用顺序：

```
/tm-generate → /qm-generate → /qm-validate → /backend-dsl-query → /form-design → /foggy-frontend-init → /frontend-component-generator → /frontend-dsl-query → /integration-test → /xiaohongshu-note
```

各环节说明：

| 顺序 | 技能 | 输入 | 输出 |
|---|---|---|---|
| 1 | `/tm-generate` | DDL 或表名 | TM 模型文件 |
| 2 | `/qm-generate` | TM 模型 | QM 查询模型 |
| 3 | `/qm-validate` | TM/QM 模型 | 模型可用性验证结果 |
| 4 | `/backend-dsl-query` | QM 模型 | Service 层查询代码 |
| 5 | `/form-design` | API 需求 | Form/DTO 类 |
| 6 | `/foggy-frontend-init` | 前端工程 | Foggy 前端基础接入 |
| 7 | `/frontend-component-generator` | QM 模型 | Vue 组件 |
| 8 | `/frontend-dsl-query` | QM 模型 | 前端查询 API 封装 |
| 9 | `/integration-test` | 已实现链路 | 集成测试或回归测试 |
| 10 | `/xiaohongshu-note` | 项目状态 | 进度笔记 |

## 增量迭代规则

当项目已有基础链路，进入增量迭代时：

- 如果用户新增了数据表 → 从 S2（TM 生成）开始
- 如果用户修改了表结构 → 更新对应 TM，然后级联更新 QM
- 如果用户只是新增查询字段或筛选能力 → 从 S3（QM 生成）或 S4（校验）开始
- 如果用户要加新功能页面 → 从 S5 或 S6 开始
- 如果用户要优化现有组件或接口 → 直接进入 S7（测试与迭代增强）

## 约束条件

- 不跳过阶段：TM 未完成不生成 QM，QM 未完成不做前端组件生成
- 不替代具体技能：本技能只做编排和状态判断，实际生成工作交给对应技能
- 状态判断基于文件实际存在情况，不依赖用户口述
- 不处理通用项目治理、版本规划、文档 fan-out、验收签收
- 每次迭代结束建议生成进度笔记，保持项目文档持续更新

## 决策规则

- 如果是新会话且用户说"继续" → 先做项目状态扫描，恢复上下文
- 如果多个阶段都有缺口 → 按 S0-S7 顺序，优先处理最早缺口
- 如果用户指定了要做的事 → 跳过自动判断，直接引导该任务
- 如果检测到 CLAUDE.md 中的 TODO 项 → 纳入迭代计划的待办清单
- 如果迭代完成 → 提醒生成进度笔记并更新 CLAUDE.md
