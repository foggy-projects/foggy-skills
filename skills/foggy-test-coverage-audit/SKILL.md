---
name: foggy-test-coverage-audit
description: 在 foggy-implementation-quality-gate 之后、foggy-acceptance-signoff 之前执行测试证据覆盖审计，检查 requirement、bug、acceptance item 与 unit、integration、e2e、playwright、manual evidence 的映射是否完整，并判断是否可进入验收。仅用于测试证据盘点，不用于代码质量检查或正式签收。
---

# Foggy Test Coverage Audit

对交付物做“测试证据覆盖审计”，而不是代码行覆盖率统计。

这个 skill 负责回答：

- 当前 requirement / bug / acceptance item 是否被足够的测试证据承接
- 缺口是在 unit、integration、e2e、playwright 还是 manual evidence
- 现在是否适合进入 `foggy-acceptance-signoff`
- 下一步应该调用哪个技能补齐缺口

它不替代真正的测试编写，也不替代正式验收。

## 使用边界

适用：
- 子模块已报告开发完成和测试通过，但在正式验收前需要复核测试覆盖是否足够
- 对某个版本目录做测试证据盘点，判断是否还有遗漏的回归保护
- 对某个功能、BUG、验收项盘点已有测试和手工验证证据
- 需要判断应该先写测试用例文档、先补失败测试、还是直接补测试代码
- 已签收后做一次回归防护复盘，识别长期仍偏弱的测试保护

不适用：
- 只是单纯编写一个测试文件
- 只是跑一次 Playwright 或 E2E
- 只是计算单个语言工具输出的代码 coverage 百分比
- 直接代替 `foggy-acceptance-signoff` 做签收

这些场景分别优先使用：
- `integration-test`
- `playwright-cli`
- 语言或项目内已有的单元测试工具
- `foggy-acceptance-signoff`

## 审计模式

### 1. `pre-acceptance-check`

默认模式。

用于功能或版本准备进入正式验收前，确认测试证据是否完整。

默认输出：

- `docs/<version>/coverage/<target>-coverage-audit.md`

### 2. `post-acceptance-regression-review`

用于签收后回头检查长期回归防护是否足够。

默认输出：

- `docs/<version>/coverage/<target>-regression-review.md`

## 核心原则

- 审计的是“证据覆盖”，不是单纯的行覆盖率或分支覆盖率。
- requirement、bug、acceptance item 都应尽量能映射到某种验证证据。
- 复杂 E2E / Playwright 流程优先检查是否存在测试用例文档，而不是只看有没有测试文件。
- BUG 修复需要重点检查是否形成长期回归保护。
- 手工验证允许存在，但不能用手工验证掩盖本应自动化覆盖的高风险场景。

## 最小输入

每次至少确认：

- 审计范围：`version` 或 `feature`
- 目标版本
- 审计对象路径或标识
- 当前阶段：`pre-acceptance-check` 或 `post-acceptance-regression-review`
- 要参考的 requirement / bug / acceptance / progress / test / evidence 路径

如果缺少版本、对象、审计范围，不要擅自补全，先问用户。

## 最小输出

每次至少产出一份 coverage audit 记录。记录至少包含：

- audit scope
- version
- target
- reviewed at / reviewed by
- requirement or bug coverage summary
- 各测试层级的已有证据
- 缺口列表
- 结论
- 下一步建议技能

## 固定输出契约

每份审计记录开头都应包含：

```yaml
---
audit_scope: version | feature
audit_mode: pre-acceptance-check | post-acceptance-regression-review
version: v1.0
target: <feature-or-version>
status: draft | reviewed | blocked
conclusion: ready-for-acceptance | ready-with-gaps | needs-more-tests | blocked-by-missing-evidence
reviewed_by: <name-or-role>
reviewed_at: YYYY-MM-DD
follow_up_required: yes | no
---
```

正文段落顺序固定为：

```markdown
# Test Coverage Audit

## Background

## Audit Basis

## Coverage Matrix

## Evidence Summary

## Gaps

## Recommended Next Skills

## Conclusion
```

## Coverage Matrix 要求

`## Coverage Matrix` 至少逐项列出：

- requirement / acceptance item / bug 标识
- 风险级别：critical / major / minor
- 现有验证层：
  - unit-test
  - integration-test
  - e2e-test
  - playwright-test
  - manual-evidence
- 证据位置
- 覆盖结论：
  - covered
  - partially-covered
  - not-covered

不要只写总评，必须能看到逐项映射。

## 推荐工作流

1. 明确审计对象
- 是整个版本
- 还是单个功能 / 子模块 / BUG 修复项

2. 收集审计依据
- requirement
- implementation plan
- progress docs
- bug work items
- acceptance checklist
- unit / integration / e2e / playwright 测试记录
- manual evidence

3. 建立覆盖映射
- requirement 对哪些测试负责承接
- BUG 修复是否已经形成回归测试
- acceptance item 是否有足够证据支撑

4. 判断缺口类型
- 缺少测试用例文档
- 缺少自动化测试
- 缺少手工验证步骤
- 测试已存在，但无法映射到 requirement / bug
- 测试通过了，但覆盖层级明显不对

5. 输出结论
- `ready-for-acceptance`
- `ready-with-gaps`
- `needs-more-tests`
- `blocked-by-missing-evidence`

6. 给出下一步技能建议
- `integration-test`
- `playwright-cli`
- `foggy-bug-regression-workflow`
- `foggy-acceptance-signoff`
- `plan-evaluator`

## 决策规则

### 什么时候先补测试用例文档

满足以下任一条件时，优先先写用例文档，再写测试代码：

- 涉及跨模块流程
- 涉及多个接口或页面联动
- 使用 Playwright 或复杂 E2E
- 验收步骤较长，容易因口头描述失真
- 多人协作，测试边界需要先对齐

### 什么时候优先先补失败测试

满足以下任一条件时，优先建议先补失败测试再修复：

- BUG 可稳定复现
- 问题属于核心链路
- 已出现过回归
- 修复后需要长期自动化保护

这类问题通常应转交：

- `foggy-bug-regression-workflow`
- 然后由 `integration-test` 或项目测试工具补具体测试

### 什么时候可以直接补测试代码

满足以下条件时，可以不单独生成用例文档，直接在现有测试文件上补测试：

- 范围小
- 行为边界清晰
- 只是补已有测试文件中的一个场景、断言或分支
- 不依赖复杂环境准备

但测试名必须能直接说明覆盖的行为；必要时加简短注释说明背景。

### 什么时候不能只靠测试代码注释

以下场景不要只在测试代码里写注释，应有独立手工记录或 evidence：

- 人工验收步骤
- 页面操作说明
- 依赖账号、权限、环境切换
- 需要给验收者复核的操作路径

## 结论判定规则

### `ready-for-acceptance`

仅当以下条件都满足时使用：

- 高风险 requirement / acceptance item 已有充分证据承接
- 关键 BUG 修复已有合理回归保护
- 必要的手工验证步骤或体验证据已齐
- 没有明显缺口会影响正式验收判断

### `ready-with-gaps`

用于主体证据已齐，但仍有非阻断性缺口：

- 缺口必须明确列出
- 必须说明是否允许带风险进入验收
- 不要把明显阻断的缺口降级到这里

### `needs-more-tests`

用于功能已接近完成，但在进入验收前仍应补测试：

- 关键场景缺少自动化测试
- 复杂流程缺 case 文档
- BUG 修复缺少回归测试
- 重要 acceptance item 没有可复核证据

### `blocked-by-missing-evidence`

用于无法判断是否可验收：

- requirement 或 acceptance basis 缺失
- 测试结果缺失
- 证据路径缺失
- 子模块报告无法映射到真实测试内容

## 与其他技能的协作

- `foggy-versioned-doc-tracking` 负责把需求、BUG、progress、test、experience 落到正确版本目录。
- `foggy-implementation-quality-gate` 负责在覆盖审计前检查实现是否达到基本质量门槛。
- `foggy-test-coverage-audit` 负责在验收前后检查这些材料是否构成足够的测试证据覆盖。
- `foggy-acceptance-signoff` 负责正式签收，不负责替代本 skill 做覆盖审计。
- `integration-test` 负责补集成测试、E2E、BUG 回归测试。
- `playwright-cli` 负责浏览器自动化执行和 Playwright 相关验证。
- `foggy-bug-regression-workflow` 负责把 BUG 转成复现与回归保护任务。
- `plan-evaluator` 可用于复核“当前建议的测试层级是否过度或不足”。

默认顺序：

`execution-checkin`
→ `foggy-implementation-quality-gate`
→ `foggy-test-coverage-audit`
→ 需要时补测试 / 补 case / 补 evidence
→ `foggy-acceptance-signoff`

## 模板

如需直接套模板，优先使用：

- `assets/templates/coverage-audit-template.md`
