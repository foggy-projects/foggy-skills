#!/usr/bin/env python3
"""Install canonical skills into Codex, Claude, or project-local agent paths."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = REPO_ROOT / "skills"

DEFAULT_TARGETS = {
    "codex": Path.home() / ".codex" / "skills",
    "claude": Path.home() / ".claude" / "skills",
    "agents": Path.cwd() / ".agents" / "skills",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Install Foggy skills for different AI clients.")
    parser.add_argument(
        "--target",
        choices=sorted(DEFAULT_TARGETS),
        required=True,
        help="Install destination type.",
    )
    parser.add_argument(
        "--path",
        type=Path,
        help="Override installation directory.",
    )
    parser.add_argument(
        "--skills",
        nargs="*",
        help="Install only the named skills. Defaults to all canonical skills.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing target skill directories.",
    )
    return parser.parse_args()


def iter_skill_names(selected: list[str] | None) -> list[str]:
    available = sorted(path.name for path in SKILLS_DIR.iterdir() if path.is_dir())
    if not selected:
        return available
    missing = sorted(set(selected) - set(available))
    if missing:
        raise ValueError(f"Unknown skills: {', '.join(missing)}")
    return sorted(selected)


def install_skill(skill_name: str, destination_root: Path, force: bool) -> None:
    source = SKILLS_DIR / skill_name
    destination = destination_root / skill_name
    if destination.exists():
        if not force:
            raise FileExistsError(f"Destination exists: {destination}")
        shutil.rmtree(destination)
    shutil.copytree(source, destination)


def main() -> int:
    args = parse_args()
    destination_root = args.path or DEFAULT_TARGETS[args.target]
    destination_root.mkdir(parents=True, exist_ok=True)

    for skill_name in iter_skill_names(args.skills):
        install_skill(skill_name, destination_root, force=args.force)

    print(f"Installed skills to {destination_root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
