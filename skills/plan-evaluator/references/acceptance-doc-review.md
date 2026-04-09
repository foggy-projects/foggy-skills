# Acceptance Doc Review

用于评审验收文档、签收结论、signoff 记录。

## 重点检查

- 验收依据是否覆盖 requirement / implementation plan / acceptance criteria
- evidence 是否足以支撑最终结论
- blocker 是否被错误降级
- `accepted-with-risks` 是否被滥用
- 结论、风险项、后续动作之间是否自洽
- 是否明确记录未完成项、开放问题、后续 owner
- 执行标准合规项是否已逐一核对：
  - 测试是否已执行并通过
  - progress 文档是否已更新
  - final report 是否已输出
  - `foggy-implementation-quality-gate` 是否已执行
  - `foggy-test-coverage-audit` 是否已执行

## 常见否决点

- 证据不足却直接签收
- 阻断项被包装成”风险可接受”
- 验收结论与测试/体验/进度材料不一致
- 应走的执行标准（quality-gate / test-coverage-audit）被跳过，且验收文档未说明原因

## 输出倾向

- 只做评审，不替代正式签收
- 如果证据不够，优先指出”待补证”，不要勉强通过
- 如果执行标准未走完，优先标记为 blocked 而不是降级为 accepted-with-risks
