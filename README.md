# Foggy Skills

Foggy Navigator 开源 Skill 仓库。仓库同时面向多种 AI 编程工具：

- Claude Code：通过 Marketplace / Plugin 包装层分发
- Codex：直接消费标准 `skills/<skill-name>/` 目录，并使用 `agents/openai.yaml`
- 其他兼容 Agent Skills 的客户端：可将 `skills/` 安装到项目内 `.agents/skills/`

## 设计原则

- `skills/` 是唯一事实源
- `catalogs/skills.json` 保存版本、分类、标签、作者等目录元数据
- `.claude-plugin/` 和 `plugins/` 是生成物，用于 Claude Marketplace 兼容
- 不要手改生成物；新增或修改 skill 时只改 `skills/` 和 `catalogs/skills.json`

## 仓库结构

```text
foggy-skills/
├── skills/                      # Canonical skills
│   └── <skill-name>/
│       ├── SKILL.md
│       ├── agents/
│       │   └── openai.yaml
│       ├── scripts/
│       ├── references/
│       └── assets/
├── catalogs/
│   └── skills.json              # Catalog metadata
├── scripts/
│   ├── build_marketplace.py     # Generate Claude marketplace wrappers
│   ├── validate_skills.py       # Validate canonical structure
│   └── install_skills.py        # Install skills for Codex / Claude / .agents
├── .claude-plugin/              # Generated marketplace index
├── plugins/                     # Generated Claude plugin wrappers
└── README.md
```

## 安装

### Claude Code Marketplace

```bash
claude plugin marketplace add foggy-projects/foggy-skills
claude plugin marketplace list
```

### Codex

```bash
python scripts/install_skills.py --target codex --force
```

默认安装到：

- Linux / macOS: `~/.codex/skills`
- Windows: `%USERPROFILE%\.codex\skills`

### Claude 本地 skills

```bash
python scripts/install_skills.py --target claude --force
```

默认安装到：

- Linux / macOS: `~/.claude/skills`
- Windows: `%USERPROFILE%\.claude\skills`

### 项目级 `.agents/skills`

```bash
python scripts/install_skills.py \
  --target agents \
  --path /path/to/project/.agents/skills \
  --force
```

## 维护命令

生成 Claude Marketplace 包装层：

```bash
python scripts/build_marketplace.py
```

校验 canonical skills 与生成物：

```bash
python scripts/validate_skills.py
python scripts/build_marketplace.py --check
```

## 维护流程

1. 在 `skills/<skill-name>/` 修改 `SKILL.md`、`scripts/`、`references/`、`assets/`
2. 在 `catalogs/skills.json` 更新该 skill 的版本、分类、标签、作者等元数据
3. 执行 `python scripts/build_marketplace.py`
4. 执行 `python scripts/validate_skills.py` 和 `python scripts/build_marketplace.py --check`
5. 提交 `skills/`、`catalogs/`、`.claude-plugin/`、`plugins/` 的变更

## 当前技能数量

当前仓库包含 29 个 skill，目录元数据统一由 `catalogs/skills.json` 管理。

## License

MIT
