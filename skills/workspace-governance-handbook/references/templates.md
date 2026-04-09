# Templates

这些是骨架，不是必须逐字照抄。应按项目结构和命名习惯收敛。

## 1. 根目录 CLAUDE.md 骨架

```markdown
# 项目总控手册

## 1. 项目定位

## 2. 当前工作区职责

## 3. 独立 agent 工作目录

## 4. 版本规划规则

## 5. 子任务下沉规则

## 6. 代码注释约定

- 当前迭代新增的 Entity、类、方法，默认补 `@since {当前版本}` 注释
- 存量代码默认不强制追补

## 7. 验收与 BUG 回流流程

## 8. 输出文件命名规则

## 9. 子 agent 提示词要求
```

## 2. 子目录 CLAUDE.md 骨架

```markdown
# {目录名} 工作手册

## 1. 目录定位

## 2. 开发目标

## 3. 必须继承的上层约束

## 4. 当前目录结构

## 5. 工作方式

## 6. 代码注释约定

- 当前迭代新增的 Entity、类、方法，默认补 `@since {当前版本}` 注释
- 存量代码默认不强制追补

## 7. 输出文件规则

## 8. 与上层任务的配合规则

## 9. 开发边界

## 10. 验证要求

## 11. 最终回复规范
```

## 3. 后端目录默认输出示例

```text
docs/{version}/{priority}-{topic}-开发进度.md
docs/{version}/bugs/{priority}-{topic}-修复反馈.md
```

## 4. 测试目录默认输出示例

```text
docs/{version}/{priority}-{topic}-测试反馈.md
docs/{version}/bugs/{priority}-{topic}-回归反馈.md
```

## 5. 前端目录可选输出示例

```text
docs/{version}/{priority}-{topic}-体验反馈.md
```
