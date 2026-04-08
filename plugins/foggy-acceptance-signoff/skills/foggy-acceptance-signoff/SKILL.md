---
name: foggy-acceptance-signoff
description: 对版本目录或单功能执行验收，汇总 requirement、implementation plan、progress、test、experience 与 evidence，生成明确的验收记录并给出签收结论。用于对版本文档目录做全量验收、对某个功能单独验收、输出 accepted or rejected or blocked 结论、或需要回写签收标记时使用。
---

# Foggy Acceptance Signoff

对已经进入交付或收口阶段的内容执行正式验收，给出可复核的签收记录。

这个 skill 不负责制定方案，也不负责推进执行。它负责回答：这次交付是否满足验收条件，证据是否完整，最终能否签收。

## 使用边界

适用：
- 对 `docs/<version>/` 下的整个版本做验收
- 对某个功能、票据、模块单独做验收
- 需要把 requirement、计划、测试、体验、证据汇总成正式验收记录
- 需要输出明确结论并回写签收状态

不适用：
- 方案还在讨论，还没有形成验收标准
- 只是更新开发进度，不需要签收结论
- 只是把 root 文档拆给各子模块落盘
- 只是做单条测试，不形成验收报告

这些场景分别优先使用：
- `plan-evaluator`
- `foggy-versioned-doc-tracking`
- `foggy-plan-execution-docs`
- `integration-test`
- `foggy-implementation-quality-gate`
- `foggy-test-coverage-audit`
- `foggy-bug-regression-workflow`

## 验收模式

### 1. `version-acceptance`

对一个版本目录整体签收。

默认读取：
- root `docs/<version>/` 下的 requirement / plan / acceptance-evidence
- 各 owning repo 的 progress / test / experience / 子模块验收记录
- 必要时读取根 README 或版本总览

默认输出：
- `docs/<version>/acceptance/version-signoff.md`

### 2. `feature-acceptance`

对某个功能、票据、子模块任务单独签收。

默认读取：
- 该功能对应的 requirement / progress / test / experience / evidence
- 如其来源于 root execution doc，额外读取对应 root requirement 和 acceptance criteria

默认输出：
- `docs/<version>/acceptance/<feature-or-ticket>-acceptance.md`

## 职责分工

- 执行侧或 owning module 负责准备验收材料，包括 requirement、implementation plan、progress、test、experience 与 evidence。
- `foggy-versioned-doc-tracking` 负责保证这些材料落在正确的版本目录和 owning repo 中，但不负责编写正式验收文档。
- `foggy-test-coverage-audit` 负责在正式验收前后，检查 requirement、bug、acceptance item 与测试证据的映射是否充分，但不替代正式签收。
- `foggy-implementation-quality-gate` 负责在覆盖审计和正式验收前检查实现质量是否达到基本门槛。
- `foggy-acceptance-signoff` 负责编写正式验收文档、形成签收结论、并在需要时回写签收标记。
- 功能级验收通常由 owning module / owning repo 侧发起并编写。
- 版本级验收通常由 root-controller、release owner 或统一签收角色发起并编写。
- 如果需要对验收结论做第二轮审视，可在产出验收文档后再调用 `plan-evaluator` 做二次评审，但它不替代正式签收。
- 如果验收过程中发现新的 BUG，应由 `foggy-acceptance-signoff` 保留缺陷结论，再转交 `foggy-bug-regression-workflow` 建立 BUG work item、判断测试回补策略与修复清单。

## 最小输入

每次至少确认：
- 验收范围：`version` 或 `feature`
- 目标版本
- 验收对象路径或标识
- 验收依据来自哪些文档
- 由谁签收，或至少由哪个角色签收
- 是否需要回写签收状态

如果缺少版本、验收范围、验收依据，不要擅自补全，先问用户。

## 最小输出

每次至少产出一份验收记录。验收记录至少包含：
- scope
- version
- status
- decision
- signoff owner / role
- 背景与目标
- 验收依据文档清单
- 验收检查项
- 证据清单
- 未通过项 / 风险项
- 最终结论

推荐同时回写签收标记到 root 文档或子模块文档。

## 固定输出契约

正式验收记录默认使用固定结构，不要自由发挥字段名或段落顺序。

如需直接套模板，优先使用：
- `assets/templates/version-signoff-template.md`
- `assets/templates/feature-acceptance-template.md`

### 1. 文档头部签收标记

每份验收记录开头都应包含一个统一标记块：

```yaml
---
acceptance_scope: version | feature
version: v1.0
target: <feature-or-version>
status: draft | in-review | signed-off | rejected | blocked
decision: accepted | accepted-with-risks | rejected | blocked
signed_off_by: <name-or-role>
signed_off_at: YYYY-MM-DD
reviewed_by: <name-or-role-or-N/A>
blocking_items: []
follow_up_required: yes | no
evidence_count: 0
---
```

字段要求：
- `status` 表示验收流程状态，`decision` 表示最终结论，两者不要混用。
- `status=signed-off` 只对应 `decision=accepted` 或 `accepted-with-risks`。
- `status=rejected` 只对应 `decision=rejected`。
- `status=blocked` 只对应 `decision=blocked`。
- `blocking_items` 填阻断项标题数组；无阻断时填 `[]`。
- `follow_up_required` 只接受 `yes` 或 `no`。
- `evidence_count` 填本次引用的有效证据条数。

### 2. 正文固定段落

正文段落顺序固定为：

```markdown
# {scope} Acceptance

## Background

## Acceptance Basis

## Checklist

## Evidence

## Risks / Open Items

## Final Decision

## Signoff Marker
```

其中 `## Signoff Marker` 需要再用清单形式重复一次最终签收状态，便于被上游 root 文档或子模块文档直接摘录。

### 2.1 模板选择规则

- 如果验收对象是整个 `docs/<version>/` 版本目录，使用 `assets/templates/version-signoff-template.md`
- 如果验收对象是某个功能、票据或单模块任务，使用 `assets/templates/feature-acceptance-template.md`
- 版本级模板必须包含 `## Module Summary`
- 功能级模板必须包含 `## Failed Items`

### 3. 回写签收标记格式

如需把结果回写到 root requirement、root execution doc、子模块 progress 或 acceptance 文档，统一使用下面这个紧凑块：

```markdown
## Acceptance Status

- acceptance_status: signed-off | rejected | blocked
- acceptance_decision: accepted | accepted-with-risks | rejected | blocked
- signed_off_by: <name-or-role>
- signed_off_at: YYYY-MM-DD
- acceptance_record: <relative-doc-path>
- blocking_items: none | item1, item2
- follow_up_required: yes | no
```

不要在回写块中复述整篇验收正文，只同步状态、结论、记录路径和阻断信息。

## 推荐工作流

1. 明确验收范围：
   - 是整个版本
   - 还是单个功能
2. 确认材料责任人和签收责任人：
   - 谁负责准备 requirement / progress / test / experience / evidence
   - 谁负责给出正式 signoff
3. 读取验收依据：
   - requirement
   - implementation plan
   - acceptance criteria
   - progress docs
   - test records
   - experience records
   - acceptance-evidence
4. 如子模块刚完成交付，优先读取最新的 `foggy-implementation-quality-gate` 结果；如还没有，可先执行实现质量检查。
5. 如测试覆盖复杂、跨层或刚完成子模块交付，优先读取最新的 `foggy-test-coverage-audit` 结果；如还没有，可先执行覆盖审计。
6. 建立验收检查表：
   - 功能完成度
   - 测试通过情况
   - 体验验证情况
   - 文档完整度
   - 依赖项闭环情况
7. 核对证据：
   - 明确哪些项有证据
   - 哪些项只有口述没有证据
   - 哪些项明确缺失
8. 形成结论：
   - `accepted`
   - `accepted-with-risks`
   - `rejected`
   - `blocked`
9. 写入验收记录。
10. 如用户要求，回写签收标记到上游 root 文档和相关子模块文档。

## 验收发现 BUG 的处理规则

当验收过程中发现 BUG 时：
- 不要在验收文档中直接展开修复方案
- 先根据影响决定本次验收结论是 `rejected`、`blocked` 或 `accepted-with-risks`
- 在 `## Risks / Open Items` 和 `## Failed Items` 中写清 BUG 摘要
- 立即转交 `foggy-bug-regression-workflow`

转交时至少带上：
- BUG 来源：`acceptance-found`
- 对应 acceptance record 路径
- 缺陷摘要
- 影响范围
- 已有证据

验收文档里只需要保留：
- BUG 摘要
- 是否阻断签收
- BUG work item 路径
- 是否需要修复后重新验收

## 结论判定规则

### `accepted`

仅当以下条件都满足时使用：
- 验收依据完整
- 必要测试结果齐全
- 必要体验验证齐全，或明确标记 `N/A`
- 没有阻断上线或交付的问题

### `accepted-with-risks`

用于核心目标达成，但仍有非阻断性遗留问题：
- 风险必须明确列出
- 必须写明后续跟进项
- 不能把明显阻断问题降级成风险项

### `rejected`

用于以下情况：
- 关键验收标准未满足
- 存在明确失败项
- 测试或体验结果表明不能签收

### `blocked`

用于以下情况：
- 验收依据不完整
- 关键证据缺失
- 无法判断是否满足验收标准

不要因为时间紧就把 `blocked` 写成 `accepted-with-risks`。

## 验收记录模板

推荐结构：

```markdown
---
acceptance_scope: version | feature
version: v1.0
target: {feature-or-version}
status: signed-off
decision: accepted
signed_off_by: {name-or-role}
signed_off_at: {YYYY-MM-DD}
reviewed_by: {name-or-role-or-N/A}
blocking_items: []
follow_up_required: no
evidence_count: 3
---

# {scope} Acceptance

## Background

## Acceptance Basis
- [doc1]
- [doc2]

## Checklist
- [x] 验收项 1
- [ ] 验收项 2

## Evidence
- 测试记录：
- 体验记录：
- 产物链接：

## Risks / Open Items

## Final Decision

## Signoff Marker
- acceptance_status: signed-off
- acceptance_decision: accepted
- signed_off_by: {name-or-role}
- signed_off_at: {YYYY-MM-DD}
- acceptance_record: docs/{version}/acceptance/{target}.md
- blocking_items: none
- follow_up_required: no
```

如果是版本级验收，额外加：
- 子模块验收汇总表
- 版本级阻塞项总表
- 最终签收说明

## 回写规则

如用户要求回写状态，至少同步这些位置：
- root requirement 或 root execution doc 的状态字段
- 对应子模块 progress 或 acceptance 文档
- 版本级 `README` 或总览文档（如果该项目已有此约定）

回写时只更新状态、链接、签收结论，不重写上游规划正文。

## 与其他技能的关系

- `workspace-governance-handbook`
  - 定义根目录总控与子目录职责边界
- `plan-evaluator`
  - 在验收前可审视方案是否合理
  - 在验收文档产出后可做二次评审，检查结论是否与依据和证据一致
- `foggy-plan-execution-docs`
  - 生成上游 requirement / plan / acceptance-evidence
- `foggy-versioned-doc-tracking`
  - 保证执行与进度材料落在正确版本目录
- `integration-test`
  - 提供测试证据

本 skill 位于这些 skill 之后，负责最终收口和签收。

## 默认保守策略

- 不编造通过结果
- 不用“开发已完成”替代“验收已通过”
- 不省略失败项或证据缺失项
- 体验验证不适用时明确写 `N/A`
- 如果只能得出部分结论，优先写 `blocked` 或 `accepted-with-risks`
