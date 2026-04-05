---
name: foggy-plan-execution-docs
description: 将已经讨论并确认可落地的跨模块或跨仓规划，拆解为可执行的版本化文档包。适用于需要把规划转成 requirement、module responsibility、code inventory、implementation plan，以及可选 execution prompt 的场景。触发词：提及“拆成执行文档”“生成开发规划”“生成代码清单”“生成开工提示词”“规划转执行”“requirement+plan”。
---

# Foggy Plan Execution Docs

当用户已经完成方案讨论，准备把规划下沉到各子模块执行时使用本 skill。

这个 skill 不负责重新发散方案，也不直接写代码。它负责把“已确认规划”转成后续 agent 可直接消费的根目录总控执行文档包。

## 适用边界

适用：

- 已确认总体方案，需要拆到多个模块或仓库
- 需要同时输出需求、职责、开发规划
- 需要提前整理代码触点，降低后续 agent 分析成本
- 需要为后续开发 agent 生成开工提示词

不适用：

- 方案还在讨论中、还没有形成共识
- 只是想记录一个 bug 或需求，不涉及执行拆解
- 已经有明确开发任务，只差具体编码

纯“版本化落盘”场景优先使用 `foggy-versioned-doc-tracking`。本 skill 关注的是“从规划到根目录总控执行文档包”，不是单纯“写到哪个版本目录”。

## 核心原则

### 1. 先拆 ownership，再写文档

先识别 root controller、owning repo、consumer repo、配套 repo，再决定文档怎么拆。

### 2. `code-inventory` 必选

如果没有代码清单，文档对后续 agent 的帮助会很弱。

### 3. `execution-prompt` 可选

不是每次都要生成开工提示词。只有用户明确需要“可以直接交给 agent 开工”的材料时才生成。

### 4. 固定 workflow，弹性输出

输出内容要稳定，但不要把文档形态写死成单一模板。允许：

- requirement 和 implementation plan 合并
- requirement 和 implementation plan 分开
- 单 root 文档
- root 下多个配套文档

前提是必备内容完整。

### 5. 默认只写 root 文档

默认只在 workspace 主目录 `docs/<version>/` 下生成总控执行文档。

只有用户明确要求时，才允许本 skill 直接写子模块文档。

## 最小输入

每次使用本 skill，至少确认这些信息：

- 当前 workspace 或相关 repo
- 已确认的目标
- 已确认的约束
- 目标版本
- 涉及的模块或仓库
- 是否需要 execution prompt

如果缺少版本、ownership 或边界，不要擅自补全，先问用户。

## 最小输出

默认生成 root 文档包。文档包至少包含下面 3 个必选块，和 1 个可选块。

### 必选 1. requirement

至少包含：

- 背景
- 目标
- 约束
- 非目标
- 验收标准

### 必选 2. module responsibility

至少包含：

- root / workspace 负责什么
- 每个子模块或仓库负责什么
- 哪些模块现在可以开工
- 哪些模块依赖前置条件

### 必选 3. code-inventory

至少包含：

- repo
- path
- role
- expected change
- notes

`expected change` 推荐使用：

- `create`
- `update`
- `read-only-analysis`
- `do-not-touch`

### 推荐 4. execution-prompt

当用户明确要“可直接交给 agent 开工”的材料，或项目会拆给多个执行 agent 时，再生成 execution-prompt。

至少包含：

- 你需要先读的文档（需求 + code-inventory + implementation-plan）
- 你需要做的事（按 Step 列出）
- 你不需要做的事（明确边界）
- 验收方式（可运行的命令或检查项）
- 执行完成后（指向 progress 模板，告知 agent 写报告）

单仓、单 agent、纯文档落盘场景可以不生成。

### 推荐 5. progress-template

当项目需要阶段性汇报、多人协作、或最终要形成验收闭环时，再生成 progress-template。

至少包含：

- 基本信息（版本、状态、上游文档链接、完成日期占位）
- 前置条件检查表（上一个 Stage 的输出是否到位）
- Development Progress（对照 implementation-plan 的每个 Step，留状态占位）
- 计划外变更（执行中新增/调整的内容）
- Testing Progress（关键验证用例表，留结果占位）
- Experience Progress（标记 N/A 或留占位）
- 需求验收标准对照（对照需求文档逐条列出）
- 阻塞项（留占位）
- 后续衔接（下一个 Stage 的前置条件是否满足）

如果只是一次性规划文档，不强制要求。

### 推荐 6. acceptance-evidence

当目标是“可执行且可签收”的版本包时，补一个验收材料块，至少明确：

- 验证步骤手册是否需要
- 验收报告是否需要
- 截图 / 日志 / 产物下载链接是否需要
- 最终签收结论写在哪个根文档

## 推荐工作流

1. 读取并压缩已确认规划，明确哪些内容是“已决定”，哪些是“待确认”。
2. 识别 ownership：
   - workspace/root
   - authority repo
   - consumer repo
   - supporting repo
3. 判断输出模式：
   - `requirement-only`（罕见，仅用于前期探索）
   - `requirement+plan`（单仓或单 agent 默认）
   - `requirement+plan+prompt+progress`（多 agent 执行模式）
   - `requirement+plan+acceptance-evidence`（交付/验收导向模式）
4. 为 root 生成总控执行文档：
   - 总目标
   - 总边界
   - 总实施顺序
5. 在 root 文档中明确后续子模块拆解目标：
   - 哪些 repo 需要正式下发文档
   - 每个 repo 需要哪些文档类型
   - 每个 repo 的代码清单和实施边界
6. 为每个子模块生成 execution prompt（含验收命令和报告指引）。
7. 为每个子模块生成 progress template（预填 Step 对照表和验收标准表）。
8. 最后检查：
   - 版本目录是否正确
   - 每个 repo 是否有 owner
   - code-inventory 是否足够具体
   - 是否和已有文档重复或冲突

## 与 `foggy-versioned-doc-tracking` 的关系

优先分工而不是合并：

- `foggy-plan-execution-docs`
  - 负责把规划拆成 root 总控执行文档包
- `foggy-versioned-doc-tracking`
  - 负责根据 root 总控文档，把内容正式落到正确 repo / version 路径

如果两者同时适用：

1. 先用本 skill 在 root `docs/<version>/` 下生成总控执行文档
2. 再按 `foggy-versioned-doc-tracking` 的路径规则，把文档正式拆解到子模块版本目录

## 代码清单写法

推荐写成结构化列表，而不是一句泛泛描述。

示例：

```yaml
code_inventory:
  - repo: foggy-model-registry
    path: scripts/publish.py
    role: bundle publish entry
    expected_change: create
    notes: first MVP script

  - repo: foggy-odoo-bridge-pro
    path: foggy_mcp_pro/setup/foggy-models
    role: temporary authority source
    expected_change: read-only-analysis
    notes: do not treat as consumer copy
```

如果还不能确认具体文件，至少要写到目录级别，并明确“后续需补充关键入口文件”。

## 输出检查清单

完成前确认：

- 已确认规划与待确认事项被区分
- ownership 已拆清
- requirement 已写
- code-inventory 已写
- 实施顺序已写
- 如启用 execution-prompt：每个目标子模块都有 prompt
- 如启用 progress-template：模板包含前置条件检查、Step 对照、验收标准对照、后续衔接
- 如启用 execution-prompt：包含"执行完成后更新 progress"的指引
- 如目标是交付签收：验收材料和最终签收落点已定义
- 默认落点是 root `docs/<version>/`
- 文档与现有版本目录规则不冲突

## 默认保守策略

- 不把所有内容硬塞进一个巨型文档
- 不默认每个模块都生成 execution prompt
- 不擅自补未确认的技术决策
- 不把“代码清单”写成空泛的模块名列表
- 不默认直接写子模块文档
