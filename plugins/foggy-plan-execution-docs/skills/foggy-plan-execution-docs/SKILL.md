---
name: foggy-plan-execution-docs
description: 将已经讨论并确认可落地的跨模块或跨仓规划，拆解为可执行的版本化文档包。适用于需要把规划转成 requirement、module responsibility、code inventory、implementation plan，以及可选 execution prompt 的场景。触发词：提及“拆成执行文档”“生成开发规划”“生成代码清单”“生成开工提示词”“规划转执行”“requirement+plan”。
---

# Foggy Plan Execution Docs

当用户已经完成方案讨论，准备把规划下沉到各子模块执行时使用本 skill。

这个 skill 不负责重新发散方案，也不直接写代码。它负责把“已确认规划”转成后续 agent 可直接消费的根目录总控执行文档包。

文档默认应优先表达：

- 这个文档是干什么的
- 谁应该使用它
- 它约束的是流程、边界、完成标准，还是验收

除非存在明确架构约束，否则不要把规划写成“手把手指定类名和包路径”的编码说明书。

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

### 2. ownership / touchpoint 必选，但默认不要写得过细

如果没有 ownership 或代码触点清单，文档对后续 agent 的帮助会很弱。

但默认应优先写到：

- repo
- module
- directory
- capability boundary

不要在规划阶段默认细化到每个类、每个包路径，除非：

- 用户明确要求
- 存在明确架构约束
- 不细化就会导致模块归属错误

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

### 6. 规划默认聚焦流程，不替子 agent 做局部设计

默认在文档中明确这些内容：

- 目标
- 与版本目标的映射关系
- 非目标
- ownership
- 前置条件
- 完成定义
- 必须补哪些测试
- 测试必须执行并通过
- 完成后需要更新哪些 progress 文档
- 完成后要跑哪些 review / audit / acceptance skill
- 如规划涉及对外 API、generated-api、前后端联调契约，还应显式识别是否存在“字段名不足以表达用法”的高风险参数或接口；若存在，规划中必须把“补契约说明”列为执行项或验收项

### 7. 安全边界跟随目标项目声明，不擅自泛化

如果目标 workspace、repo 或 module 的 `CLAUDE.md` 已声明当前阶段的安全边界，执行文档必须显式继承这些约束，或明确写出本次哪些安全事项不在范围内。

这里要求的是“沿用目标项目已声明规范”，不是把某个项目的具体安全实现模式上升为通用模板。像 `TenantXxxLoader` 这类项目内约定，只能在该项目文档里作为本地规范出现，不能在本 skill 中写成所有项目默认必须采用的实现。

默认不要替子 agent 预判：

- `Form/Result` 到底放 `common` 还是业务模块
- 单个功能内部应该拆几个 package
- 每个类的最终命名

这些细节优先由子 agent 按当前目录结构和 `CLAUDE.md` 自主决定。

## 最小输入

每次使用本 skill，至少确认这些信息：

- 当前 workspace 或相关 repo
- 已确认的目标
- 已确认的约束
- 目标版本
- 涉及的模块或仓库
- 是否需要 execution prompt

如果当前任务属于某个版本或迭代，还必须先确认：

- 是否已有版本目标 / 迭代目标 / 成功标准文档
- 当前准备下沉的执行包支撑的是哪个版本目标
- 如果没有版本目标基线，是否需要先补版本目标再继续拆执行文档

如果缺少版本、ownership 或边界，不要擅自补全，先问用户。

## 最小输出

默认生成 root 文档包。文档包至少包含下面 3 个必选块，和 1 个可选块。

所有文档在最前面都应明确“文档作用”。推荐使用如下起始结构：

```markdown
# 文档标题

## 文档作用

- doc_type: requirement | implementation-plan | progress | execution-prompt | acceptance
- intended_for: root-controller | sub-agent | reviewer | signoff-owner
- purpose: 用一句话说明这个文档的用途
```

### 必选 1. requirement

至少包含：

- 背景
- 与版本目标的关系
- 目标
- 约束
- 非目标
- 验收标准
- 若涉及外部消费契约，还应写明哪些参数或接口存在特殊格式要求、预处理要求或兼容限制，避免执行 agent 自行猜测

### 必选 2. module responsibility

至少包含：

- root / workspace 负责什么
- 每个子模块或仓库负责什么
- 哪些模块现在可以开工
- 哪些模块依赖前置条件
- 当前执行包分别支撑哪个版本目标或成功标准

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

**模块归属验证（强制）：**

为每个 `create` 类型的文件，必须验证其目标模块是否正确：

1. **读取目标模块的 CLAUDE.md 或 pom.xml**，理解项目自己的分层规则
2. **检查模块间依赖方向**：如果编排 Service 需要注入多个 impl 模块的 Bean，必须检查是否会产生循环依赖
3. **循环依赖的处理**：
   - 如果 A-impl 已依赖 B-impl，编排逻辑不能放在 B-impl
   - 此时应创建独立的编排模块（如 `*-platform-impl`），该模块可依赖所有 impl 模块
   - 编排模块只放跨域编排逻辑，不放单域业务
4. **`*-cloud-service` 是部署壳**，禁止放 Service / Controller / 编排逻辑 / Form / Result——只保留启动类和集成测试
5. 只有在 `CLAUDE.md` 或现有架构明确要求时，才在规划里指定精确代码落点
6. 对 `Form / Result / DTO / VO` 的最终归属，默认交由子 agent 按模块 `CLAUDE.md` 和当前目录结构决定；规划阶段只需避免明显错误归属

### 推荐 4. execution-prompt

当用户明确要“可直接交给 agent 开工”的材料，或项目会拆给多个执行 agent 时，再生成 execution-prompt。

至少包含：

- 你需要先读的文档（需求 + code-inventory + implementation-plan）
- 你需要做的事（按 Step 列出）
- 你不需要做的事（明确边界）
- 验收方式（可运行的命令或检查项）
- 你需要遵守的本模块 `CLAUDE.md`
- 完成后需要执行的 review / audit / acceptance skill
- **完成定义（强制）**：明确告知子 agent，"编写测试"不等于"完成"，必须：
  1. 编译通过（`mvn compile`）
  2. **运行全部测试并通过**（`mvn test`），不允许跳过失败的测试
  3. 如果测试需要外部环境（DB、MQ 等）且当前不可用，必须在 progress 中明确标注"测试未运行"及原因，不得标记为"已完成"
  4. 如有测试失败，必须修复后重新运行，直到全部通过才可标记为完成
- **体验验证要求（UI 功能强制）**：如果本次任务涉及 UI 交互（页面、表单、列表、弹窗、导航等），必须：
  1. 生成体验检查清单（见下方"体验清单生成规则"）
  2. 编写 playwright 自动化测试覆盖核心交互流程
  3. playwright 测试必须运行通过
  4. 手工走查可作为补充，但不能替代 playwright 自动化证据
  5. 如果功能纯后端 / 纯 API / 无 UI，标记 `experience: N/A` 并写明原因
- 执行完成后（指向 progress 模板，告知 agent 写报告）

单仓、单 agent、纯文档落盘场景可以不生成。

### 体验清单生成规则

当功能涉及 UI 交互时，execution-prompt 或 progress-template 中必须包含体验检查清单。

**判断标准**——以下任一条件满足即视为"涉及 UI 交互"：

- 新增或修改页面、路由
- 新增或修改表单、列表、弹窗、抽屉
- 新增或修改按钮交互、状态切换
- 新增或修改数据展示（表格、详情、卡片）
- 涉及权限控制的 UI 可见性变化

**体验清单默认维度**：

- 页面可达性：目标页面能否正常加载，路由是否正确
- 核心交互流程：主链路操作（增删改查/提交/取消）是否正常完成
- 表单验证：必填校验、格式校验、边界值是否正确触发
- 异常状态：空数据、加载中、请求失败时 UI 是否合理
- 权限可见性：不同角色下按钮/菜单/数据的显隐是否符合预期
- 数据一致性：操作后列表/详情数据是否实时刷新且正确

**playwright 覆盖要求**：

- 每个体验清单维度至少有一个 playwright test case 覆盖
- playwright 测试必须可独立运行、可重复执行
- 测试通过记录作为验收 evidence 的一部分
- 如果 playwright 运行环境不可用，必须在 progress 中标注"playwright 未运行"及原因，不得标记体验验证完成

### 推荐 5. progress-template

当项目需要阶段性汇报、多人协作、或最终要形成验收闭环时，再生成 progress-template。

至少包含：

- 基本信息（版本、状态、上游文档链接、完成日期占位）
- 前置条件检查表（上一个 Stage 的输出是否到位）
- Development Progress（对照 implementation-plan 的每个 Step，留状态占位）
- 计划外变更（执行中新增/调整的内容）
- Testing Progress（关键验证用例表，留结果占位）
- Experience Progress：
  - 如功能涉及 UI：体验检查清单 + playwright 测试状态表（用例名 / 覆盖维度 / pass|fail|not-run）
  - 如功能纯后端 / 无 UI：标记 `N/A` 并写明原因
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

1. 读取并压缩已确认规划，明确哪些内容是”已决定”，哪些是”待确认”。
2. **读取目标模块的 CLAUDE.md 或等价文档**，理解模块内部分层、目录结构、开发约束，以及当前阶段已声明的安全边界。
3. 识别 ownership：
   - workspace/root
   - authority repo
   - consumer repo
   - supporting repo
4. 判断输出模式：
   - `requirement-only`（罕见，仅用于前期探索）
   - `requirement+plan`（单仓或单 agent 默认）
   - `requirement+plan+prompt+progress`（多 agent 执行模式）
   - `requirement+plan+acceptance-evidence`（交付/验收导向模式）
5. **模块依赖与归属检查**（code-inventory 生成前必须完成）：
   - 检查目标仓库的 pom.xml 依赖方向（A-impl → B-impl 是否已存在）
   - 判断编排 Service 是否涉及多个 impl 模块的 Bean 注入
   - 如存在循环依赖风险，规划独立编排模块（如 `*-platform-impl`）
   - 如只涉及单个 impl 模块，编排逻辑放该 impl 模块
   - `*-cloud-service` 只放启动类和集成测试，不放 Controller / Service / Form / Result
   - 精确到 package / class 的落点，只有在架构约束明确时才写入文档
6. 为 root 生成总控执行文档：
   - 总目标
   - 总边界
   - 与目标 `CLAUDE.md` 一致的安全边界或安全非目标
   - 总实施顺序
   - 完成定义
   - 必测项
   - 执行完成后的 review / audit / acceptance 流程
7. 在 root 文档中明确后续子模块拆解目标：
   - 哪些 repo 需要正式下发文档
   - 每个 repo 需要哪些文档类型
   - 每个 repo 的代码清单和实施边界
8. 为每个子模块生成 execution prompt（含验收命令和报告指引）。
9. 为每个子模块生成 progress template（预填 Step 对照表和验收标准表）。
10. 最后检查：
   - 版本目录是否正确
   - 每个 repo 是否有 owner
   - code-inventory 是否足够支持后续 agent 判断 ownership，但没有过度细化实现
   - **每个 `create` 文件的模块归属是否符合层级约束**
   - **是否存在循环依赖风险**
   - **如果 `CLAUDE.md` 声明了安全边界，文档是否已继承对应约束或明确列出本次不覆盖的安全非目标**
   - **是否错误地把某个项目专属安全实现模式写成通用强制方案**
   - 文档开头是否明确写明“文档作用”
   - 是否明确了测试执行通过、progress 回写、最终报告、后置评审 skill
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
  - repo: authority-repo
    path: scripts/publish.py
    role: bundle publish entry
    expected_change: create
    notes: first MVP script

  - repo: consumer-repo
    path: app/setup/models
    role: temporary authority source
    expected_change: read-only-analysis
    notes: do not treat as consumer copy
```

如果还不能确认具体文件，优先写到模块或目录级别，并明确“后续由执行 agent 按 `CLAUDE.md` 决定具体落点”。

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
- 文档开头已明确写出其作用和使用对象

## 默认保守策略

- 不把所有内容硬塞进一个巨型文档
- 不默认每个模块都生成 execution prompt
- 不擅自补未确认的技术决策
- 不把“代码清单”写成空泛的模块名列表
- 不默认指定具体类名、package 名、`Form/Result` 精确归属
- 不默认直接写子模块文档
- 不把某个项目专属安全实现细节上升成通用模板；只要求文档遵循目标项目 `CLAUDE.md` 已声明的安全边界
