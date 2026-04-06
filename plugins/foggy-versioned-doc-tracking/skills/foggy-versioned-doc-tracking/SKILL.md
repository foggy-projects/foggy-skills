---
name: foggy-versioned-doc-tracking
description: Use when working in a multi-repo or multi-module workspace and the user asks to record a bug, requirement, optimization, or cross-project follow-up into versioned project docs, or to update development, testing, and experience progress in the correct owning module.
---

# Foggy Versioned Doc Tracking

Use this skill when the task is not "just write a note", but "put the note in the right repo, under the right version, and keep progress traceable".

When a root-level execution doc already exists, treat it as the upstream source of truth for submodule doc fan-out.

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

Default workflow in that case:

1. Read the root doc under workspace `docs/<version>/`
2. Split by ownership
3. Create or update versioned docs in each owning repo
4. Cross-link the root doc and submodule docs

Do not rewrite the root plan unless the user explicitly asks.

## Repo Convention Discovery

Do not hardcode repo names, folder names, or ticket prefixes from a previous project. First inspect the current workspace and determine which of these patterns applies.

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
3. Select the operation mode:
   - `record`
   - `progress-update`
   - `execution-checkin`
4. Classify the item:
   - bug
   - requirement
   - optimization
   - cross-project coordination
5. Create or update the versioned doc in the owning repo.
6. Create or update progress tracking so development, testing, and experience are traceable.
7. For cross-project issues, create one owning doc per repo and cross-link them.
8. If a doc was created in the wrong version or wrong folder, move it and remove the stale copy.

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

- version
- priority / severity
- status
- background
- root cause or problem statement
- target outcome
- task split / ownership
- acceptance criteria
- constraints / non-goals

### Progress Tracking

Always make sure these three dimensions are visible somewhere:

- development progress
- testing progress
- experience progress

When the doc is derived from a root execution plan (via `foggy-plan-execution-docs`), the progress doc should also include:

- 前置条件检查表（上一个 Stage 的输出是否到位）
- Step 逐条对照（对照 implementation-plan 的每个 Step 标注完成状态）
- 计划外变更（执行中新增/调整的内容）
- 需求验收标准对照（对照需求文档逐条列出）
- 阻塞项（如有阻塞，记录原因和依赖）
- 后续衔接（下一个 Stage 的前置条件是否满足）

Allowed shapes:

- In Odoo prompt docs: use `<ticket-prefix>-progress.md`
- In Java/Python staged work: use `dev-logs/`, `test-records/`, and optional `experience/`
- For execution-plan derived work: use `<doc-prefix>-progress.md` with full template
- For smaller items: one compact progress doc is acceptable if it still covers all three dimensions

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

