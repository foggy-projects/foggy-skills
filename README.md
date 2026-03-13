# Foggy Skills

Foggy Navigator 开源 Skill 插件市场 — 为 Claude Code 提供可复用的 AI 编程技能集。

## 插件列表

| 插件 | 分类 | 说明 |
|------|------|------|
| backend-dsl-query | development | 引导后端使用 DSL 查询数据，生成 Java Service 层代码 |
| build-and-push | devops | 项目构建部署（Docker/CI-CD） |
| dsl-syntax-guide | development | DSL 查询语法参考手册 |
| foggy-frontend-init | development | 初始化前端 Foggy 开发环境 |
| foggy-java-integration | development | Java/Spring Boot 集成 Foggy Dataset Model |
| foggy-model-workflow | development | TM/QM 模型开发工作流编排 |
| foggy-project-iteration | development | 项目迭代向导 |
| form-design | development | Spring Boot Form/DTO 设计规范 |
| frontend-component-generator | development | 自动生成 Vue 业务组件 |
| frontend-dsl-query | development | 前端 DSL 查询接口生成 |
| frpc-remote-manage | devops | 远程 frpc 配置管理 |
| mongo-model-dev | development | MongoDB 数据模型开发 |
| mysql-docker-client | devops | Docker 容器化 MySQL 客户端 |
| plan-evaluator | utility | 技术方案评估与风险分析 |
| preagg-cache-optimize | development | 预聚合与缓存优化 |
| qm-generate | development | 根据 TM 生成 QM 查询模型 |
| qm-schema-viewer | development | 查看 QM schema 信息 |
| qm-validate | development | 验证 TM/QM 模型文件 |
| skill-creator | development | 创建完整技能（含脚本/资源/打包） |
| skill-writer | development | 快速生成 SKILL.md 文件 |
| spring-api-doc | development | Spring Controller API 文档生成 |
| syntho | utility | 私有代码库智能检索 |
| tm-generate | development | 根据 DDL 生成 TM 表模型（JDBC） |
| tm-generate-mongo | development | 根据 MongoDB 集合生成 TM 表模型 |
| tm-syntax-reference | development | TM 语法参考手册 |
| xiaohongshu-note | utility | 生成小红书风格项目进度笔记 |

## 安装

### 方式一：配置 settings.json（推荐）

在 `~/.claude/settings.json` 中添加 marketplace 配置：

```json
{
  "foggy-skills": {
    "source": {
      "source": "git",
      "url": "https://github.com/foggy-projects/foggy-skills.git"
    }
  }
}
```

> **注意**：如果文件中已有其他配置（如 `company-skill-marketplace`），直接追加 `foggy-skills` 键即可，多个 marketplace 可共存。

重启 Claude Code 后技能会自动加载。

### 方式二：手动克隆

```bash
# Linux / macOS
git clone https://github.com/foggy-projects/foggy-skills.git \
  ~/.claude/skills/foggy-skills

# Windows (PowerShell)
git clone https://github.com/foggy-projects/foggy-skills.git `
  "$env:USERPROFILE\.claude\skills\foggy-skills"

# 验证
cat ~/.claude/skills/foggy-skills/.claude-plugin/marketplace.json
```

## 目录结构

```
foggy-skills/
├── .claude-plugin/
│   └── marketplace.json           # 插件注册表（26 个插件）
├── plugins/
│   └── {plugin-name}/
│       ├── .claude-plugin/
│       │   └── plugin.json        # 插件元数据
│       └── skills/
│           └── {skill-name}/
│               ├── SKILL.md       # 技能指令（必需）
│               ├── scripts/       # 可执行脚本（可选）
│               └── references/    # 参考文档（可选）
└── README.md
```

## License

MIT
