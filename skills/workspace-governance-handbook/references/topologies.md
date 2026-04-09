# Topologies

本文件用于帮助判断当前工作区属于哪种结构，不要把“多个目录”自动等同于“微服务”。

## 1. 单仓多模块

```text
project/
  backend-a/
  backend-b/
  web/
  tests/
```

建议：
- 根目录作为 `root-controller`
- `backend-a` / `backend-b` 作为 `backend-module`
- `web` 作为 `frontend-module` 或 `web-aggregator`
- `tests` 作为 `test-suite`

## 2. 多个相关 Git 项目共处一个工作区

```text
workspace/
  core-platform/.git
  admin-web/.git
  mobile-app/.git
  shared-sdk/.git
  tests/
```

特点：
- 目录之间有业务关系
- 但未必是微服务
- 往往由一个总控层统一规划与验收

建议：
- `workspace` 可作为 `root-controller`
- 各独立 Git 项目作为独立 agent 工作目录
- `shared-sdk` 多数情况下是 `shared-library`
- `tests` 作为 `test-suite`

## 3. 单体项目 + 辅助目录

```text
project/
  server/
  ui/
  scripts/
  docs/
```

建议：
- `project` 作为 `root-controller`
- `server` 作为 `backend-module`
- `ui` 作为 `frontend-module`
- `scripts` 通常不需要独立 handbook，除非承担独立测试或构建职责

## 4. 纯后端工作区

```text
project/
  service-a/
  service-b/
  sdk/
  tests/
```

建议：
- 不要求存在 web 层
- `sdk` 多数情况下作为 `shared-library`

## 5. 纯前端工作区

```text
project/
  admin/
  mobile/
  component-lib/
  tests/
```

建议：
- `admin` / `mobile` 作为 `frontend-module`
- `component-lib` 作为 `shared-library`
- `tests` 作为 `test-suite`

## 6. 判断“是否值得独立一个 handbook”

满足任一项，通常值得独立：
- 目录承担独立开发任务
- 目录可以单独验证或单独发布
- 目录有明确边界和负责人
- 目录会接收上层任务并回写结果
- 目录已有自己的 Git 仓库

不满足这些条件时，可以不独立，继续由上级目录 handbooks 覆盖。
