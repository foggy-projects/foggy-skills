---
acceptance_scope: feature
version: v1.0
target: feature-or-ticket-id
doc_role: acceptance-record
doc_purpose: 说明本文件用于功能级正式验收与签收结论记录
status: signed-off
decision: accepted
signed_off_by: module-owner
signed_off_at: YYYY-MM-DD
reviewed_by: N/A
blocking_items: []
follow_up_required: no
evidence_count: 0
---

# Feature Acceptance

## Document Purpose

- doc_type: acceptance
- intended_for: signoff-owner / reviewer / owning-module
- purpose: 记录功能级正式验收结论与证据摘要

## Background

- Version: v1.0
- Target: feature-or-ticket-id
- Owner: owning-module / owning-repo
- Goal: 说明该功能或票据的交付目标和验收边界。

## Acceptance Basis

- [feature requirement]
- [feature implementation plan]
- [progress record]
- [test record]
- [experience record]
- [acceptance evidence]

## Checklist

- [ ] scope 内功能点已全部交付
- [ ] 原始 acceptance criteria 已逐项覆盖
- [ ] 关键测试已通过
- [ ] 体验验证已完成，或明确标记 `N/A`
- [ ] 文档、配置、依赖项已闭环

## Evidence

- Requirement:
  - <requirement-doc-path>
- Test:
  - <test-doc-path>
- Experience:
  - <experience-doc-path>
- Artifact:
  - <artifact-path-or-link>

## Failed Items

- none

## Risks / Open Items

- none

## Final Decision

结论写法要求：
- 明确写出该功能是 `accepted`、`accepted-with-risks`、`rejected` 还是 `blocked`
- 如果存在遗留风险，必须列出 owner 和 follow-up

## Signoff Marker

- acceptance_status: signed-off
- acceptance_decision: accepted
- signed_off_by: module-owner
- signed_off_at: YYYY-MM-DD
- acceptance_record: docs/v1.0/acceptance/feature-or-ticket-id-acceptance.md
- blocking_items: none
- follow_up_required: no
