#!/usr/bin/env python3
"""Validate canonical skills metadata and structure."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = REPO_ROOT / "skills"
CATALOG_PATH = REPO_ROOT / "catalogs" / "skills.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate canonical Foggy skills.")
    parser.add_argument(
        "--check-generated",
        action="store_true",
        help="Also require generated marketplace artifacts to be up to date.",
    )
    return parser.parse_args()


def load_catalog() -> dict:
    if not CATALOG_PATH.exists():
        raise FileNotFoundError("Missing catalogs/skills.json")
    return json.loads(CATALOG_PATH.read_text(encoding="utf-8"))


def parse_frontmatter(skill_md: Path) -> dict[str, str]:
    content = skill_md.read_text(encoding="utf-8")
    match = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n", content, re.S)
    if not match:
        raise ValueError(f"Missing YAML frontmatter in {skill_md}")
    fields: dict[str, str] = {}
    for raw_line in match.group(1).splitlines():
        if ":" not in raw_line:
            continue
        key, value = raw_line.split(":", 1)
        fields[key.strip()] = value.strip().strip('"').strip("'")
    return fields


def validate_catalog_structure(catalog: dict) -> None:
    required_root = ["name", "description", "owner", "license", "skills"]
    missing = [key for key in required_root if key not in catalog]
    if missing:
        raise ValueError(f"Catalog missing required keys: {', '.join(missing)}")
    if not isinstance(catalog["skills"], list) or not catalog["skills"]:
        raise ValueError("Catalog skills must be a non-empty array")


def validate_skills(catalog: dict) -> None:
    seen_names: set[str] = set()
    skill_dirs = {path.name: path for path in sorted(SKILLS_DIR.iterdir()) if path.is_dir()}
    catalog_names = []

    for entry in catalog["skills"]:
        required = ["name", "description", "version", "category", "author", "tags"]
        missing = [key for key in required if key not in entry]
        if missing:
            raise ValueError(f"Skill {entry.get('name', '<unknown>')} missing keys: {', '.join(missing)}")
        name = entry["name"]
        if name in seen_names:
            raise ValueError(f"Duplicate skill name in catalog: {name}")
        seen_names.add(name)
        catalog_names.append(name)

        if name not in skill_dirs:
            raise ValueError(f"Canonical skill directory is missing: skills/{name}")

        skill_md = skill_dirs[name] / "SKILL.md"
        if not skill_md.exists():
            raise ValueError(f"Missing SKILL.md in skills/{name}")

        frontmatter = parse_frontmatter(skill_md)
        if frontmatter.get("name") != name:
            raise ValueError(f"Frontmatter name mismatch in {skill_md}")
        if frontmatter.get("description") != entry["description"]:
            raise ValueError(
                f"Description mismatch for {name}: SKILL.md and catalogs/skills.json must match"
            )

    extra_dirs = sorted(set(skill_dirs) - set(catalog_names))
    if extra_dirs:
        raise ValueError(f"Catalog missing entries for: {', '.join(extra_dirs)}")


def main() -> int:
    args = parse_args()
    catalog = load_catalog()
    validate_catalog_structure(catalog)
    validate_skills(catalog)

    if args.check_generated:
        result = subprocess.run(
            [sys.executable, str(REPO_ROOT / "scripts" / "build_marketplace.py"), "--check"],
            cwd=REPO_ROOT,
            check=False,
        )
        if result.returncode != 0:
            raise RuntimeError("Generated marketplace artifacts are stale")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
