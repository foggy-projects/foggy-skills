---
name: foggy-bug-regression-workflow
description: 对用户报告或验收发现的 BUG 建立标准处理流程，完成问题记录、复现判断、测试回补决策、修复清单与代码关联。用于报告 BUG、验收发现缺陷、需要先建立失败测试再修复、或需要判断是否必须补单元测试或集成测试时使用。
---

# Foggy Bug Regression Workflow

对 BUG 执行标准化收口流程，回答三个问题：

- 这个问题是否被清晰记录并可复现
- 这次修复是否需要先补测试还原
- 修复完成后如何避免同类问题再次出现

这个 skill 不替代具体编码技能，也不替代正式验收。它负责把 BUG 从“口头问题”变成“可执行的修复任务”。

## 使用边界

适用：
- 用户直接报告 BUG
- 验收过程中发现新的缺陷
- 回归测试发现历史问题复发
- 需要先补失败测试，再进入修复
- 需要为 BUG 建立修复清单、代码关联、验证策略

不适用：
- 还没有确认是否真的是 BUG，只是方案讨论
- 已经是明确的新功能需求，不是缺陷修复
- 只是更新版本进度，不需要 BUG 级别的记录

这些场景分别优先使用：
- `plan-evaluator`
- `foggy-versioned-doc-tracking`
- `foggy-plan-execution-docs`

## 上下游关系

- `foggy-versioned-doc-tracking` 负责把 BUG 文档落到正确版本目录，但不负责复现与测试策略判断。
- `foggy-bug-regression-workflow` 负责把 BUG 转成标准 work item，并给出测试决策与修复清单。
- `integration-test` 或项目内的单元测试技能，负责真正创建测试还原。
- `foggy-acceptance-signoff` 在验收发现 BUG 时，应把缺陷转交给本 skill，而不是在验收文档里直接展开修复流程。
- 如需复核测试决策或修复策略，可再调用 `plan-evaluator`。

## 最小输入

每次至少确认：
- 目标版本
- BUG 来源：`user-report` / `acceptance-found` / `regression-found`
- 问题现象
- 影响范围
- 当前是否可稳定复现
- 是否已经有相关测试或历史缺陷记录

如果缺少版本、问题现象、来源，不要擅自补全，先问用户。

## 最小输出

每次至少产出一份 BUG work item，默认放在：

- `docs/<version>/workitems/BUG-<slug>.md`

文档至少包含：
- 来源与背景
- 复现条件
- 期望结果 / 实际结果
- 影响范围
- 测试策略
- 代码关联
- 修复清单
- 验证方式
- 当前状态

如需直接套模板，优先使用：
- `assets/templates/bug-workitem-template.md`

## 固定字段

每份 BUG work item 开头都应包含：

```yaml
---
type: bug
bug_source: user-report | acceptance-found | regression-found
version: v1.0
ticket: BUG-001
severity: critical | major | minor | trivial
status: open | in-progress | ready-for-verification | closed | waived
reproduction_status: confirmed | partial | unknown | cannot-reproduce
test_strategy: pending | unit-test | integration-test | e2e-test | manual-evidence-only
automation_decision: required | optional | waived
owner: <name-or-role>
---
```

字段要求：
- `test_strategy` 描述优先验证层级。
- `automation_decision` 描述这次是否必须补自动化测试。
- `status=waived` 只用于确认本次不继续处理，并写明原因。

## 推荐工作流

1. 建立 BUG 条目
- 统一记录来源、环境、现象、影响范围
- 如果 BUG 来自验收，写清来自哪份 acceptance record

2. 做复现判断
- 是否有稳定步骤
- 是否有明确输入、环境、前置数据
- 是否能得到一致的失败结果

3. 做测试决策
- 业务逻辑可隔离：优先 `unit-test`
- 跨层调用、接口、数据读写：优先 `integration-test`
- 前端交互、完整流程：优先 `e2e-test`
- 无法合理自动化：允许 `manual-evidence-only`，但必须说明原因

4. 生成修复清单
- 关联代码路径
- 标注预期修改类型
- 列出修复步骤
- 列出验证步骤

5. 修复后回写状态
- 测试是否补齐
- BUG 是否复现消失
- 是否需要重新进入 `foggy-acceptance-signoff`

## 测试决策规则

### `automation_decision=required`

满足以下任一条件时，默认要求先补测试或同时补测试：
- 已出现过回归
- 核心业务链路
- 问题可稳定复现
- 修复逻辑较集中，可被单测或集成测试覆盖

### `automation_decision=optional`

适用于：
- 风险较低
- 改动简单
- 自动化测试成本明显高于收益

### `automation_decision=waived`

仅在这些情况允许：
- 热修时效极高，当前先止血
- 问题强依赖外部环境，短期无法稳定自动化
- 项目当前没有对应测试基础设施，且本次改动极小

使用 `waived` 时必须补：
- 原因
- 风险
- 是否留后续补测事项

## 与验收 skill 的协作

如果 BUG 来源是验收：
- `foggy-acceptance-signoff` 负责保留验收结论
- 本 skill 负责新建 BUG work item
- 验收记录里只保留 BUG 摘要、阻断状态和 BUG work item 路径
- 修复完成后，再回到 `foggy-acceptance-signoff` 重新验收

不要把完整修复方案直接塞进验收文档正文。

## 建议模板

推荐结构：

```markdown
---
type: bug
bug_source: acceptance-found
version: v1.0
ticket: BUG-001
severity: major
status: open
reproduction_status: confirmed
test_strategy: integration-test
automation_decision: required
owner: backend-module
---

# BUG Work Item

## Background

## Reproduction

## Expected vs Actual

## Impact Scope

## Test Strategy

## Code Inventory

## Fix Checklist

## Verification

## References
```

