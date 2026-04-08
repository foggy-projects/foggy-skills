---
name: foggy-implementation-quality-gate
description: 对子模块或单功能在 execution-checkin 之后执行开发质量闸门检查，聚焦实现收口、重复与复杂度、可读性、关键逻辑注释、风险和文档回写，判断是否可进入 foggy-test-coverage-audit。仅用于实现质量复核，不用于测试覆盖审计、方案评审或正式验收。
---

# Foggy Implementation Quality Gate

对“已经开发完成”的结果做实现质量闸门检查。

这个 skill 不替代 lint、测试执行、覆盖审计或正式验收。它负责回答：

- 这次实现是否真正收口到 requirement / bug scope
- 当前代码是否存在明显质量问题、遗漏项或交付风险
- 当前结果是否已经达到进入 `foggy-test-coverage-audit` 的门槛

## 参考模式

本 skill 的设计吸收以下成熟实践的思路，但不要求项目必须接入这些工具：

- SonarQube 的 quality gate：先定义门槛，再判断能否继续流转
- reviewdog 的 diff-based review：优先聚焦实际改动面，不做无边界的泛查
- Danger 的 PR etiquette automation：把“容易忘的检查项”固定成规则
- pre-commit 的 staged checks：把质量问题尽量拦在更早阶段

如需查看这些外部模式的简要参考，读取：

- `references/quality-gate-patterns.md`

## 使用边界

适用：
- 子模块报告“开发完成、测试通过”后，做一轮实现质量复核
- BUG 修复完成后，确认修复范围、残余风险、回写和自检是否到位
- 在进入 `foggy-test-coverage-audit` 前，先判断是否仍有明显实现问题
- 多 agent 协作时，对子模块交付物做统一质量门槛检查

不适用：
- 方案还在讨论，没有代码或落地结果
- 只是跑一次 lint 或单个测试命令
- 只是做正式验收签收
- 只是统计测试证据覆盖

这些场景分别优先使用：
- `plan-evaluator`
- 项目内 lint / build / test 命令
- `foggy-acceptance-signoff`
- `foggy-test-coverage-audit`

## 质量门模式

### 1. `pre-coverage-audit`

默认模式。

用于实现完成后、进入测试覆盖审计前。

默认输出：

- `docs/<version>/quality/<target>-implementation-quality.md`

### 2. `post-fix-quality-review`

用于 BUG 修复完成后的实现质量复核。

默认输出：

- `docs/<version>/quality/<target>-fix-quality-review.md`

## 最小输入

每次至少确认：

- 检查范围：`feature` / `bug` / `module`
- 目标版本
- 对应 requirement、bug work item 或 progress doc
- 本次实际代码改动路径或模块
- 开发侧自报的完成状态、自检结果、测试结果

如果缺少版本、对象、改动范围，不要擅自补全，先问用户。

## 最小输出

每次至少产出一份质量检查记录，至少包含：

- scope
- version
- target
- changed code paths
- 质量检查项
- 发现的问题 / 风险
- 结论
- 是否可进入 `foggy-test-coverage-audit`

## 固定输出契约

每份质量检查记录开头都应包含：

```yaml
---
quality_scope: feature | bug | module
quality_mode: pre-coverage-audit | post-fix-quality-review
version: v1.0
target: <feature-or-bug-or-module>
status: draft | reviewed | blocked
decision: ready-for-coverage-audit | ready-with-risks | needs-fix-before-audit | blocked-by-quality-issues
reviewed_by: <name-or-role>
reviewed_at: YYYY-MM-DD
follow_up_required: yes | no
---
```

正文段落顺序固定为：

```markdown
# Implementation Quality Gate

## Background

## Check Basis

## Changed Surface

## Quality Checklist

## Findings

## Risks / Follow-ups

## Recommended Next Skills

## Decision
```

## Quality Checklist 要求

`## Quality Checklist` 至少覆盖这些维度：

- scope conformance
  - 是否只改了该改的
  - 是否漏了必须改的
- code hygiene
  - 是否残留 debug、临时注释、临时分支、明显 TODO
- duplication and consolidation
  - 是否出现重复实现、重复判断、重复查询拼装、重复转换逻辑
  - 是否应提取公共函数、公共模块或统一适配层
- complexity and abstraction
  - 复杂度是否已经高到需要引入更清晰的抽象
  - 是否存在适合用策略、工厂、适配器、模板方法、状态机等模式收口的重复分支或条件分派
- error handling and edge cases
  - 异常、空值、边界输入、兼容处理是否合理
- readability and maintainability
  - 命名、结构、函数长度、层级深度是否仍可快速理解
  - 是否存在“虽然能跑，但后续难维护”的实现
- critical logic documentation
  - 关键业务规则、边界条件、兼容原因、临时约束是否有必要的注释
  - 注释是否解释“为什么”，而不是重复“代码做了什么”
- contract and compatibility
  - 接口、配置、数据契约、迁移、调用方兼容是否考虑到
- documentation and writeback
  - progress、quality、test、acceptance 需要的回写是否齐
- test alignment
  - 已跑的测试是否真和改动面匹配
  - 不是看覆盖够不够，而是看测试是否明显失焦
- release readiness
  - 是否还存在阻止进入覆盖审计的实现问题

## 推荐工作流

1. 确认实现对象
- 功能开发
- BUG 修复
- 子模块交付

2. 读取依据
- requirement / bug work item
- implementation plan
- progress doc
- execution check-in
- changed files / modules
- 已执行的 lint / build / test 结果

3. 做质量检查
- 范围是否收口
- 改动是否完整
- 是否出现可收敛的重复实现
- 复杂度是否已经提示需要统一抽象或设计模式
- 关键逻辑是否需要补充注释或结构重整
- 是否有明显实现缺陷或交付遗漏
- 是否需要先补文档、迁移、配置说明

4. 记录问题
- 阻断问题
- 风险项
- 建议修复项
- 哪些问题不影响进入下一步，哪些问题必须先改

5. 输出下一步
- `foggy-test-coverage-audit`
- `foggy-bug-regression-workflow`
- `plan-evaluator`
- 回到实现阶段继续修复

## 决策规则

### `ready-for-coverage-audit`

仅当以下条件都满足时使用：

- requirement / bug scope 基本收口
- 改动面和宣称完成内容一致
- 无明显阻断性的实现问题
- 必要文档回写已完成或已明确记录
- 当前结果适合进入测试覆盖审计

### `ready-with-risks`

用于主体实现已可继续，但仍有非阻断性风险：

- 风险必须明确列出
- 不能把明显漏改、错改、兼容性问题降级到这里
- 必须说明这些风险是否允许带入覆盖审计

### `needs-fix-before-audit`

用于实现已接近完成，但在进入覆盖审计前应先修一轮：

- 有明显漏改
- 有明显重复实现，应先收敛
- 复杂度显著上升但没有合理抽象，导致可读性或维护性明显下降
- 自检不完整
- 改动面与 requirement / bug 不匹配
- 文档、迁移、配置回写缺失
- 测试虽然通过，但和改动面明显不对应

### `blocked-by-quality-issues`

用于当前交付结果无法被有效审查：

- requirement / progress / changed files 对不上
- 缺少关键依据
- 代码改动范围不明
- 实现复杂度和结构问题已严重影响审查和后续维护判断
- 存在明显阻断风险，不适合继续流转

## 可读性与抽象判断规则

出现以下信号时，不要只给“能工作就行”的结论，应明确提示收敛：

- 同类分支逻辑在多个文件重复出现
- 一个函数或方法同时承担规则判断、数据转换、异常兜底、外部调用多个职责
- 条件分支持续增加，新增需求只能继续堆 `if/else`
- 相同契约映射在前后端、不同模块或多个调用方重复维护
- 审阅时很难用几句话说清楚关键流程

此时应优先考虑：

- 提取公共 helper 或 domain service
- 用策略模式收口多分支规则
- 用工厂或适配器统一不同来源或不同实现
- 用模板方法或管道拆开固定步骤
- 用状态机表达复杂状态流转

是否真的要引入设计模式，取决于复杂度是否已达到“继续堆分支会更糟”的程度；不要为了模式而模式。

## 注释规则

关键逻辑存在以下情况时，应建议补注释：

- 业务规则并不直观
- 有历史兼容包袱
- 看起来像多余分支，但其实不能删
- 某个边界处理是为防止特定回归
- 临时方案需要明确退出条件

注释要求：

- 优先解释为什么这样做
- 必要时说明对应 requirement / bug / compatibility 背景
- 不要把显而易见的代码动作重复写成注释

## 与其他技能的协作

- `foggy-versioned-doc-tracking` 负责在执行结束时产出 `execution-checkin`，这是本 skill 的上游输入之一。
- `foggy-implementation-quality-gate` 负责检查实现质量，不直接替代测试和验收。
- `foggy-test-coverage-audit` 负责在实现质量通过后，检查测试证据是否足够。
- `foggy-acceptance-signoff` 负责正式签收。
- `foggy-bug-regression-workflow` 负责当发现缺陷修复方式不稳妥时，把问题拉回 BUG 工作流。
- `plan-evaluator` 负责在“当前实现是否过度设计 / 是否需要换实现策略”有争议时做评审。

默认顺序：

`execution-checkin`
→ `foggy-implementation-quality-gate`
→ `foggy-test-coverage-audit`
→ `foggy-acceptance-signoff`

## 模板

如需直接套模板，优先使用：

- `assets/templates/implementation-quality-gate-template.md`
