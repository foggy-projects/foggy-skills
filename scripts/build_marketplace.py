#!/usr/bin/env python3
"""Build generated marketplace artifacts from canonical skills metadata."""

from __future__ import annotations

import argparse
import filecmp
import json
import re
import shutil
import tempfile
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = REPO_ROOT / "skills"
PLUGINS_DIR = REPO_ROOT / "plugins"
CLAUDE_PLUGIN_DIR = REPO_ROOT / ".claude-plugin"
MARKETPLACE_PATH = CLAUDE_PLUGIN_DIR / "marketplace.json"
CATALOGS_DIR = REPO_ROOT / "catalogs"
CATALOG_PATH = CATALOGS_DIR / "skills.json"
ROOT_LICENSE = REPO_ROOT / "LICENSE"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build Claude marketplace wrappers from canonical skills."
    )
    parser.add_argument(
        "--bootstrap-catalog",
        action="store_true",
        help="Create catalogs/skills.json from the existing skills and marketplace.json if missing.",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check whether generated files are up to date without modifying them.",
    )
    return parser.parse_args()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def dump_json(data: dict) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2) + "\n"


def iter_skill_dirs() -> list[Path]:
    if not SKILLS_DIR.exists():
        return []
    return sorted(path for path in SKILLS_DIR.iterdir() if path.is_dir())


def parse_frontmatter(skill_dir: Path) -> dict[str, str]:
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        raise FileNotFoundError(f"Missing SKILL.md: {skill_md}")
    content = skill_md.read_text(encoding="utf-8")
    match = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n", content, re.S)
    if not match:
        raise ValueError(f"Missing YAML frontmatter in {skill_md}")
    fields: dict[str, str] = {}
    for raw_line in match.group(1).splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, value = line.split(":", 1)
        fields[key.strip()] = value.strip().strip('"').strip("'")
    if not fields.get("name") or not fields.get("description"):
        raise ValueError(f"Frontmatter in {skill_md} must contain name and description")
    return fields


def title_case_token(token: str) -> str:
    uppercase_tokens = {
        "ai",
        "api",
        "ci",
        "cd",
        "cli",
        "claude",
        "codex",
        "dsl",
        "dto",
        "frp",
        "frpc",
        "jdbc",
        "json",
        "mcp",
        "mit",
        "mongo",
        "mongodb",
        "mysql",
        "qm",
        "sql",
        "ssh",
        "spring",
        "tm",
        "ui",
        "vue",
    }
    return token.upper() if token in uppercase_tokens else token.capitalize()


def derive_display_name(skill_name: str) -> str:
    return " ".join(title_case_token(token) for token in skill_name.split("-"))


def shorten_description(description: str, limit: int = 56) -> str:
    trimmed = description.strip()
    sentence_split = re.split(r"[。！？.!?]", trimmed, maxsplit=1)
    candidate = sentence_split[0].strip() or trimmed
    if len(candidate) <= limit:
        return candidate
    return candidate[: limit - 1].rstrip() + "…"


def build_openai_yaml(skill: dict) -> str:
    interface = dict(skill.get("interface", {}))
    interface.setdefault("display_name", derive_display_name(skill["name"]))
    interface.setdefault("short_description", shorten_description(skill["description"]))

    lines = ["interface:"]
    order = [
        "display_name",
        "short_description",
        "icon_small",
        "icon_large",
        "brand_color",
        "default_prompt",
    ]
    for key in order:
        value = interface.get(key)
        if value:
            escaped = str(value).replace("\\", "\\\\").replace('"', '\\"')
            lines.append(f'  {key}: "{escaped}"')
    return "\n".join(lines) + "\n"


def load_catalog() -> dict:
    if not CATALOG_PATH.exists():
        raise FileNotFoundError(
            "Missing catalogs/skills.json. Run build_marketplace.py --bootstrap-catalog first."
        )
    return load_json(CATALOG_PATH)


def bootstrap_catalog_if_needed() -> dict | None:
    if CATALOG_PATH.exists():
        return None
    if not sources_available_for_bootstrap():
        raise FileNotFoundError("Cannot bootstrap catalog: missing skills/ or marketplace.json")

    existing_marketplace = load_json(MARKETPLACE_PATH)
    existing_plugins = {entry["name"]: entry for entry in existing_marketplace.get("plugins", [])}
    license_name = "MIT" if ROOT_LICENSE.exists() else "UNLICENSED"

    skills = []
    for skill_dir in iter_skill_dirs():
        frontmatter = parse_frontmatter(skill_dir)
        plugin = existing_plugins.get(skill_dir.name, {})
        skills.append(
            {
                "name": skill_dir.name,
                "description": frontmatter["description"],
                "version": plugin.get("version", "1.0.0"),
                "category": plugin.get("category", "development"),
                "tags": plugin.get("tags", []),
                "author": plugin.get(
                    "author",
                    existing_marketplace.get(
                        "owner",
                        {"name": "unknown", "email": "unknown@example.com"},
                    ),
                ),
                "license": license_name,
            }
        )

    catalog = {
        "name": existing_marketplace.get("name", "foggy-skills"),
        "description": existing_marketplace.get(
            "description", "Foggy Navigator 开源 Skill 合集"
        ),
        "owner": existing_marketplace.get(
            "owner", {"name": "unknown", "email": "unknown@example.com"}
        ),
        "license": license_name,
        "skills": skills,
    }
    CATALOGS_DIR.mkdir(parents=True, exist_ok=True)
    CATALOG_PATH.write_text(dump_json(catalog), encoding="utf-8")
    return catalog


def sources_available_for_bootstrap() -> bool:
    return SKILLS_DIR.exists() and MARKETPLACE_PATH.exists()


def catalog_index(catalog: dict) -> dict[str, dict]:
    return {skill["name"]: skill for skill in catalog.get("skills", [])}


def validate_catalog_against_skills(catalog: dict) -> list[dict]:
    skills_by_name = catalog_index(catalog)
    canonical_dirs = {skill_dir.name: skill_dir for skill_dir in iter_skill_dirs()}

    missing_catalog = sorted(set(canonical_dirs) - set(skills_by_name))
    missing_dirs = sorted(set(skills_by_name) - set(canonical_dirs))
    if missing_catalog or missing_dirs:
        problems = []
        if missing_catalog:
            problems.append(f"Missing catalog entries: {', '.join(missing_catalog)}")
        if missing_dirs:
            problems.append(f"Missing canonical skill directories: {', '.join(missing_dirs)}")
        raise ValueError("; ".join(problems))

    ordered = []
    for name in sorted(skills_by_name):
        skill = dict(skills_by_name[name])
        frontmatter = parse_frontmatter(canonical_dirs[name])
        if frontmatter["name"] != name:
            raise ValueError(
                f"Frontmatter name mismatch in {canonical_dirs[name] / 'SKILL.md'}: "
                f"{frontmatter['name']} != {name}"
            )
        if frontmatter["description"] != skill["description"]:
            raise ValueError(
                f"Catalog description mismatch for {name}. "
                f"Update SKILL.md or catalogs/skills.json so they match."
            )
        ordered.append(skill)
    return ordered


def marketplace_payload(catalog: dict, skills: list[dict]) -> dict:
    return {
        "$schema": "https://anthropic.com/claude-code/marketplace.schema.json",
        "name": catalog["name"],
        "description": catalog["description"],
        "owner": catalog["owner"],
        "plugins": [
            {
                "name": skill["name"],
                "description": skill["description"],
                "version": skill["version"],
                "author": skill["author"],
                "source": f"./plugins/{skill['name']}",
                "category": skill["category"],
                "tags": skill.get("tags", []),
            }
            for skill in skills
        ],
    }


def plugin_payload(skill: dict) -> dict:
    return {
        "name": skill["name"],
        "version": skill["version"],
        "description": skill["description"],
        "author": skill["author"],
        "license": skill.get("license", "UNLICENSED"),
        "keywords": skill.get("tags", []),
    }


def ensure_openai_yaml(skill: dict, check: bool) -> None:
    target = SKILLS_DIR / skill["name"] / "agents" / "openai.yaml"
    expected = build_openai_yaml(skill)
    if check:
        if not target.exists():
            raise RuntimeError(f"Missing generated file: {target}")
        actual = target.read_text(encoding="utf-8")
        if actual != expected:
            raise RuntimeError(f"Generated file is stale: {target}")
        return
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(expected, encoding="utf-8")


def build_expected_tree(base_dir: Path, catalog: dict, skills: list[dict]) -> None:
    generated_marketplace = marketplace_payload(catalog, skills)
    marketplace_dir = base_dir / ".claude-plugin"
    marketplace_dir.mkdir(parents=True, exist_ok=True)
    (marketplace_dir / "marketplace.json").write_text(
        dump_json(generated_marketplace), encoding="utf-8"
    )

    plugins_root = base_dir / "plugins"
    plugins_root.mkdir(parents=True, exist_ok=True)
    for skill in skills:
        plugin_root = plugins_root / skill["name"]
        skill_root = plugin_root / "skills" / skill["name"]
        shutil.copytree(SKILLS_DIR / skill["name"], skill_root)
        plugin_meta_dir = plugin_root / ".claude-plugin"
        plugin_meta_dir.mkdir(parents=True, exist_ok=True)
        (plugin_meta_dir / "plugin.json").write_text(
            dump_json(plugin_payload(skill)), encoding="utf-8"
        )


def compare_trees(actual: Path, expected: Path) -> list[str]:
    if not actual.exists():
        return [f"Missing path: {actual}"]
    if not expected.exists():
        return [f"Missing expected path: {expected}"]

    differences: list[str] = []

    def walk(left: Path, right: Path) -> None:
        comparison = filecmp.dircmp(left, right)
        for name in sorted(comparison.left_only):
            differences.append(f"Unexpected path: {left / name}")
        for name in sorted(comparison.right_only):
            differences.append(f"Missing path: {left / name}")
        for name in sorted(comparison.diff_files):
            differences.append(f"Different file: {left / name}")
        for name in sorted(comparison.funny_files):
            differences.append(f"Unreadable file: {left / name}")
        for child in sorted(comparison.common_dirs):
            walk(left / child, right / child)

    walk(actual, expected)
    return differences


def build_generated_outputs(catalog: dict, skills: list[dict], check: bool) -> None:
    for skill in skills:
        ensure_openai_yaml(skill, check=check)

    with tempfile.TemporaryDirectory() as temp_dir_name:
        temp_dir = Path(temp_dir_name)
        build_expected_tree(temp_dir, catalog, skills)

        if check:
            plugin_diff = compare_trees(PLUGINS_DIR, temp_dir / "plugins")
            claude_diff = compare_trees(CLAUDE_PLUGIN_DIR, temp_dir / ".claude-plugin")
            differences = plugin_diff + claude_diff
            if differences:
                raise RuntimeError("\n".join(differences))
            return

        if PLUGINS_DIR.exists():
            shutil.rmtree(PLUGINS_DIR)
        if CLAUDE_PLUGIN_DIR.exists():
            shutil.rmtree(CLAUDE_PLUGIN_DIR)

        shutil.copytree(temp_dir / "plugins", PLUGINS_DIR)
        shutil.copytree(temp_dir / ".claude-plugin", CLAUDE_PLUGIN_DIR)


def main() -> int:
    args = parse_args()
    if args.bootstrap_catalog:
        bootstrap_catalog_if_needed()

    catalog = load_catalog()
    canonical_skills = validate_catalog_against_skills(catalog)
    build_generated_outputs(catalog, canonical_skills, check=args.check)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
