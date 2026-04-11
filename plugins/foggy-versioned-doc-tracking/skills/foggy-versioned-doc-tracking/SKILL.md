---
name: foggy-versioned-doc-tracking
description: Use when working in a multi-repo or multi-module workspace and the user asks to record a bug, requirement, optimization, or cross-project follow-up into versioned project docs, or to update development, testing, and experience progress in the correct owning module.
---

# Foggy Versioned Doc Tracking

Use this skill when the task is not "just write a note", but "put the note in the right repo, under the right version, and keep progress traceable".

When a root-level execution doc already exists, treat it as the upstream source of truth for submodule doc fan-out.

默认不替执行 agent 设计具体代码结构。这个 skill 负责把任务放到正确的版本目录，并把执行流程、完成标准、测试与进度跟踪要求落盘。

## Delivery Modes

Choose the lightest mode that still preserves traceability.

### 1. `single-root-delivery`

Use this for projects that are not tiny, but also do not have clear microservice-style repo or capability boundaries.

This is the default when:

- work mainly happens in one repo or one main workspace
- requirement and bug records still need versioned tracking
- bug fixes may require reproduction and test decisions
- execution needs a development checklist, code links, and compact acceptance
- there is no real need to fan out docs into multiple owning repos

Recommended doc shape:

- `docs/<version>/workitems/<ticket-or-topic>.md`
- `docs/<version>/acceptance/<ticket-or-topic>-acceptance.md`
- optional version summary or release signoff in the same version root

In this mode:

- keep one main work item doc as the source of truth
- keep one progress section or progress companion doc for execution tracking
- link to code paths directly instead of splitting by repo ownership
- use `foggy-bug-regression-workflow` when a bug needs reproduction or test-decision support
- use `foggy-acceptance-signoff` in `feature-acceptance` mode for compact signoff

### 2. `multi-owner-delivery`

Use this when work must be split across multiple owning repos or modules.

This mode aligns with root execution docs produced by `foggy-plan-execution-docs` and fan-out into submodule docs.

Default rule:

- if ownership is clear and isolated by repo or module, use `multi-owner-delivery`
- otherwise start with `single-root-delivery` and only escalate when the work genuinely needs fan-out

## Operation Modes

Choose one of these modes before writing docs:

### 1. `record`

Use when the item is being created or formally accepted into a version:

- create the main doc
- create the initial progress skeleton if execution is expected
- link the item to the right repo / version / owner

### 2. `progress-update`

Use when execution is ongoing and the user wants the current state reflected:

- update development / testing / experience progress
- update blockers, deviations, or next steps
- keep the current progress doc aligned with what has actually happened

### 3. `execution-checkin`

Use when a coding task has just been executed or is about to be handed off:

- summarize completed work
- record touched code paths
- fill the self-check checklist
- record test status
- mark whether the item is ready for acceptance, still blocked, or needs follow-up

Default rule:

- if the user starts a coding task with this skill, begin with `record`
- if code was implemented in the same task, do not end with code only; also perform `execution-checkin`

## Upstream Source Rule

If the user has already generated a root execution doc via `foggy-plan-execution-docs`, use that root doc as the baseline.

If the current project is marked in `CLAUDE.md` as `single-root delivery` or an equivalent baseline mode, do not introduce root-controller or child-repo fan-out structure unless the user explicitly asks to escalate.

Default workflow in that case:

1. Read the root doc under workspace `docs/<version>/`
2. Split by ownership
3. Create or update versioned docs in each owning repo
4. Cross-link the root doc and submodule docs

Do not rewrite the root plan unless the user explicitly asks.

## Repo Convention Discovery

Do not hardcode repo names, folder names, or ticket prefixes from a previous project. First inspect the current workspace and determine which of these patterns applies.

Before choosing a repo convention, also inspect `CLAUDE.md` if present. If it declares a project delivery mode, treat that as the default operating context for doc placement and tracking depth.

If `CLAUDE.md` also declares the current stage security boundary, preserve that boundary in the tracked docs: inherit mandatory constraints, and keep explicitly out-of-scope security items out of the acceptance baseline unless the user asks to expand scope.

### 1. Prompt-driven repo

If a repo already uses a prompt/task-doc convention, follow that local convention.

Common signals:

- docs live under a path like `docs/prompts/<version>/`
- there is a versioned `README.md` catalog
- task docs and progress docs are paired
- experience docs are separated under `experience/`

Typical outputs:

- Main task doc: `<ticket>.md`
- Progress doc: `<ticket-prefix>-progress.md`
- Experience doc: `experience/<ticket-prefix>-experience.md` when the work is user-facing, admin-facing, or needs manual walkthrough validation

### 2. Version-root repo

If a repo mainly organizes docs by release/version folder, default to `docs/<version>/` or the repo's equivalent version root.

Typical outputs:

- Main requirement/optimization doc in the version root
- For multi-stage work, add or reuse a feature folder with:
  - `dev-logs/`
  - `test-records/`
  - `experience/` only if the item has real user/admin/manual verification value

Possible naming examples:

- Main doc: `<priority>-<topic>-需求.md` or `<topic>-优化.md`
- Dev log: `S{stage}-{YYYYMMDD}-{topic}.md`
- Test record: `T{stage}-{YYYYMMDD}-{topic}.md`

### 3. Emerging or mixed-convention repo

If the repo has no strong established pattern yet:

- prefer `docs/<version>/`
- keep the main doc in the version root
- add `dev-logs/`, `test-records/`, and optional `experience/` only when the item becomes multi-stage or requires explicit tracking
- document the chosen pattern in the version README or doc header so later work stays consistent

## Intake Workflow

1. Identify the owning repo or repos.
2. Identify the target version. Do not invent a version if the user has not given one.
3. Determine the delivery mode:
   - `single-root-delivery`
   - `multi-owner-delivery`
4. Select the operation mode:
   - `record`
   - `progress-update`
   - `execution-checkin`
5. Classify the item:
   - bug
   - requirement
   - optimization
   - cross-project coordination
6. Create or update the versioned doc in the owning repo.
7. Create or update progress tracking so development, testing, and experience are traceable.
8. For cross-project issues, create one owning doc per repo and cross-link them.
9. If a doc was created in the wrong version or wrong folder, move it and remove the stale copy.

When the delivery mode is `single-root-delivery`:

- prefer one work item doc in the version root or `workitems/`
- keep code links, checklist, test decision, and acceptance readiness in the same doc or a compact companion progress doc
- do not split by repo ownership unless the work has actually crossed a meaningful boundary
- if the item is a bug, decide whether to invoke `foggy-bug-regression-workflow` for reproduction and regression-test planning

When the delivery mode is `multi-owner-delivery`:

- split by actual ownership
- cross-link the root execution doc and submodule docs
- keep submodule progress and acceptance readiness aligned with the root plan

When a root execution doc exists, insert these checks between steps 4 and 5:

- verify the submodule doc is derived from the root ownership split
- verify the target repo really owns that part of the work
- verify the code touchpoints in the submodule doc do not drift from the root code inventory

When mode is `record` and the item is expected to enter coding:

- create the progress skeleton immediately instead of waiting until coding finishes
- prefill self-check placeholders so the execution agent can close the loop later

When mode is `execution-checkin`:

- treat missing progress writeback as incomplete delivery
- if code changed, progress docs should also reflect what changed, what was checked, and what remains

## Minimum Content

### Main Doc

Always include:

- document purpose header at the top
- version
- priority / severity
- status
- background
- root cause or problem statement
- target outcome
- task split / ownership
- acceptance criteria
- constraints / non-goals
- required review / audit / acceptance workflow when applicable

Recommended header:

```markdown
# 标题

## 文档作用

- doc_type: workitem | progress | acceptance | bug | optimization
- intended_for: execution-agent | reviewer | signoff-owner
- purpose: 一句话说明用途
```

For `single-root-delivery`, also prefer these fields when applicable:

- source type: feature / bug / optimization / acceptance-found issue
- touched code areas
- bug reproduction status
- automation decision: required / optional / waived
- execution checklist
- acceptance readiness

### Progress Tracking

Always make sure these three dimensions are visible somewhere:

- development progress
- testing progress
- experience progress

**Experience Progress 判断规则**：

功能涉及 UI 交互时（新增/修改页面、表单、列表、弹窗、按钮交互、数据展示、权限可见性变化），experience progress 不能标 `N/A`，必须包含：

- 体验检查清单（覆盖维度：页面可达性、核心交互流程、表单验证、异常状态、权限可见性、数据一致性）
- playwright 测试状态表（用例名 / 覆盖维度 / pass|fail|not-run）
- playwright 测试必须运行通过，作为验收 evidence
- 如 playwright 环境不可用，须标注原因，不得标记体验验证完成

功能纯后端 / 纯 API / 无 UI 时，标记 `experience: N/A` 并写明原因即可。

When the doc is derived from a root execution plan (via `foggy-plan-execution-docs`), the progress doc should also include:

- 前置条件检查表（上一个 Stage 的输出是否到位）
- Step 逐条对照（对照 implementation-plan 的每个 Step 标注完成状态）
- 计划外变更（执行中新增/调整的内容）
- 需求验收标准对照（对照需求文档逐条列出）
- 阻塞项（如有阻塞，记录原因和依赖）
- 后续衔接（下一个 Stage 的前置条件是否满足）
- 后置评审要求（例如 `foggy-implementation-quality-gate`、`foggy-test-coverage-audit`、`foggy-acceptance-signoff`）

Allowed shapes:

- In Odoo prompt docs: use `<ticket-prefix>-progress.md`
- In Java/Python staged work: use `dev-logs/`, `test-records/`, and optional `experience/`
- For execution-plan derived work: use `<doc-prefix>-progress.md` with full template
- For smaller items: one compact progress doc is acceptable if it still covers all three dimensions

For `single-root-delivery`, a compact shape is preferred by default:

- work item main doc with embedded `## Progress Tracking`
- or `workitems/<ticket>.md` plus `workitems/<ticket>-progress.md`

Do not force separate `dev-logs/`, `test-records/`, or `experience/` folders unless the work becomes multi-stage or the repo already uses them.

### Execution Check-in Block

When the user has executed coding work, the progress doc should also include a compact execution check-in block containing:

- completed work summary
- touched code paths or modules
- self-check checklist
- test execution status
- remaining risks / blockers
- acceptance readiness

Recommended checklist items:

- requirement or bug scope was implemented as intended
- non-goals were not accidentally expanded
- code paths updated are listed
- basic self-review was completed
- test status is recorded as pass / fail / not-run / N/A
- docs or follow-up items are recorded if still needed
- progress and final report writeback are completed

`execution-checkin` can be appended to an existing progress doc; it does not require a separate file if the current progress doc is already structured enough.

经验教训：有 progress template 的模块，子 agent 更容易产出详尽且结构化的完成报告，审阅者也更容易直接判断完成度。没有 template 的模块，报告更容易缺失或内容不全。因此在 fan-out 子模块文档时，如果存在 execution-prompt，必须同时生成 progress template。

## Decision Rules

- Respect the repo's existing naming style before introducing a new one.
- Prefer version folders over root-level temporary notes.
- Do not scatter the same issue across multiple ad hoc files in one repo.
- When the issue is cross-project, split by ownership instead of writing one giant mixed note.
- When experience tracking does not naturally apply, explicitly mark it as `N/A` rather than omitting it.
- When a root execution doc exists, prefer fan-out from that doc instead of rewriting ownership from scratch in each repo.
- Never assume another workspace uses the same repo names, path layout, or ticket prefixes as the last project you worked on.
- If this skill is used at coding start, create the progress skeleton up front.
- If code was implemented, update progress before finishing the task; do not wait for the user to remind you.
- Treat missing self-check or test status as an incomplete progress update.
- Treat missing document-purpose header as a doc-quality issue that should be corrected.
- In `single-root-delivery`, prefer one compact work item record over a multi-file doc tree unless the task complexity justifies expansion.
- If `CLAUDE.md` declares the current project mode, follow that mode by default and record only the level of structure that mode requires.

## Output Checklist

Before finishing, verify:

- the doc lives under the correct repo and version
- the naming matches local convention
- development, testing, and experience tracking are accounted for
- linked cross-project docs point to the right paths
- stale misplaced docs were removed if you moved anything
- if a root execution doc exists, the submodule doc still matches its ownership split and code inventory
- if an execution-prompt exists for the submodule, a matching progress-template also exists
- the progress-template includes Step-by-step completion tracking, acceptance criteria checklist, and downstream readiness check
- if coding was executed, the progress doc now includes completed work, self-check, and test status
- if the project is in `single-root-delivery`, the doc structure stayed compact and did not introduce unnecessary fan-out
- the doc header clearly states the document purpose and intended audience
- if the owning repo or module `CLAUDE.md` declares a security boundary, the tracked doc reflects the same in-scope and out-of-scope security assumptions
