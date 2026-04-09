---
acceptance_scope: version
version: v1.0
target: release-v1.0
doc_role: acceptance-record
doc_purpose: 说明本文件用于版本正式验收与签收结论记录
status: signed-off
decision: accepted
signed_off_by: release-owner
signed_off_at: YYYY-MM-DD
reviewed_by: N/A
blocking_items: []
follow_up_required: no
evidence_count: 0
---

# Version Acceptance

## Document Purpose

- doc_type: acceptance
- intended_for: signoff-owner / reviewer / root-controller
- purpose: 记录版本级正式验收结论与证据摘要

## Background

- Version: v1.0
- Scope: full release
- Goal: 说明本版本验收覆盖的范围、目标和交付边界。

## Acceptance Basis

- [root requirement]
- [implementation plan]
- [module responsibility]
- [test records]
- [experience records]
- [acceptance evidence]

## Module Summary

| Module | Owner | Status | Acceptance Record | Notes |
|---|---|---|---|---|
| module-a | owner-a | signed-off | docs/v1.0/acceptance/module-a.md | none |
| module-b | owner-b | signed-off | docs/v1.0/acceptance/module-b.md | none |

## Checklist

- [ ] 所有 scope 内模块均已完成 feature-level acceptance
- [ ] root requirement 中的 acceptance criteria 已覆盖
- [ ] 测试记录完整且结果可追溯
- [ ] 体验验证完整，或明确标记 `N/A`
- [ ] 阻断项已清零，或明确列在 blocker 列表中

## Evidence

- Test:
  - <test-doc-path>
- Experience:
  - <experience-doc-path>
- Delivery Artifacts:
  - <artifact-path-or-link>

## Blocking Items

- none

## Risks / Open Items

- none

## Final Decision

结论写法要求：
- 明确写出本版本是 `accepted`、`accepted-with-risks`、`rejected` 还是 `blocked`
- 如果不是 `accepted`，必须写明原因和下一步动作

## Signoff Marker

- acceptance_status: signed-off
- acceptance_decision: accepted
- signed_off_by: release-owner
- signed_off_at: YYYY-MM-DD
- acceptance_record: docs/v1.0/acceptance/version-signoff.md
- blocking_items: none
- follow_up_required: no
