# Quality Gate Patterns

以下是设计 `foggy-implementation-quality-gate` 时参考的成熟模式，用来借鉴思路，而不是要求项目必须原样接入。

## 1. SonarQube quality gates

参考：
- https://docs.sonarsource.com/sonarqube-server/quality-standards-administration/managing-quality-gates/introduction-to-quality-gates

吸收的点：
- 先定义质量门条件，再决定能否继续流转
- 质量门的核心问题是“现在是否适合继续进入下一阶段”
- 对新代码建立更明确的门槛，比对整个存量代码更实用

## 2. reviewdog

参考：
- https://github.com/reviewdog/reviewdog

吸收的点：
- 优先聚焦实际 diff，而不是全仓无限扩散
- 把工具结果挂回改动面，方便开发者直接处理
- 让检查结果和改动上下文绑定

## 3. Danger JS

参考：
- https://danger.systems/js/guides/getting_started
- https://github.com/danger/danger-js

吸收的点：
- 把“容易忘的规则”自动化、结构化
- 质量检查不只看代码，还看 PR / 交付过程完整性
- 适合承载检查清单、流程约束和提醒

## 4. pre-commit

参考：
- https://pre-commit.com/

吸收的点：
- 能前置的质量检查尽量前置
- 不同阶段可以运行不同检查
- `pre-commit run --all-files`、`--from-ref` 这种“按范围运行”的思路，适合映射到按改动面审查

## 在本地 skill 中的落地方式

这里不直接复制这些工具，而是抽成适合当前文档驱动流程的规则：

- 先有 `execution-checkin`
- 再做 `implementation quality gate`
- 再做 `test coverage audit`
- 最后才进入 `acceptance signoff`

这样“实现质量”和“测试覆盖充分性”被拆成两个相邻但不同的门。
