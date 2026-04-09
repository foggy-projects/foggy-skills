# Execution Doc Review

用于评审下沉到 owning repo 或 owning module 的执行文档。

适用对象包括：

- requirement
- implementation plan
- execution prompt
- progress 模板

## 重点检查

- 当前子模块目标是否清楚
- 非目标与边界是否清楚
- 完成定义是否够硬
- 是否明确需要补哪些测试
- 是否明确”测试必须运行通过”
- 是否明确 progress 回写、最终报告、后置 review / audit / acceptance 流程
- 是否过度锁死实现细节，压缩子 agent 合理自主空间
- 文档开头是否已声明”文档作用 / intended_for / purpose”
- 是否要求子 agent 先读取本模块 CLAUDE.md，以本模块约束为准
- 如果指定了代码落点（类名、包路径），是否交叉验证过目标模块的分层约束
- 如果测试依赖外部环境，是否明确”不可用时须在 progress 标注原因，不得标记完成”

## 常见否决点

- 只有任务，没有完成标准
- 写了测试，但没要求执行通过
- 缺少 progress / final report / 后置评审链
- 过度写死代码落点，替子 agent 做局部设计
- 指定的代码归属与目标模块 CLAUDE.md 分层约束冲突

## 输出倾向

- 优先评价”是否可直接下发执行”
- 如果阻塞项很少，建议明确指出只需收口哪几处
- 如果实现细节过密，建议精简到”目标 + 边界 + 完成标准”，把实现决策权交给子 agent
