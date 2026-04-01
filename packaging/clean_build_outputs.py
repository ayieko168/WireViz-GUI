"""Remove generated build and packaging outputs from the repository.

Usage examples:
  ./venv/Scripts/python.exe packaging/clean_build_outputs.py
  ./venv/Scripts/python.exe packaging/clean_build_outputs.py --include-caches
  ./venv/Scripts/python.exe packaging/clean_build_outputs.py --dry-run
"""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP_NAME = "WireVizStudio"


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Clean generated build outputs")
    parser.add_argument(
        "--include-caches",
        action="store_true",
        help="Also remove local test/lint/coverage caches",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Only print what would be removed",
    )
    return parser.parse_args()


def _base_cleanup_paths() -> list[Path]:
    return [
        ROOT / "build",
        ROOT / "dist",
        ROOT / "dist-artifacts",
        ROOT / f"{APP_NAME}.spec",
    ]


def _cache_paths() -> list[Path]:
    return [
        ROOT / ".coverage",
        ROOT / ".coverage.*",
        ROOT / ".pytest_cache",
        ROOT / ".ruff_cache",
    ]


def _expand_paths(paths: list[Path]) -> list[Path]:
    expanded: list[Path] = []
    for path in paths:
        if "*" in str(path):
            expanded.extend(path.parent.glob(path.name))
        else:
            expanded.append(path)
    return expanded


def _remove_path(path: Path, dry_run: bool) -> tuple[bool, str]:
    if not path.exists():
        return False, "missing"
    if dry_run:
        return True, "would remove"
    if path.is_dir():
        shutil.rmtree(path)
    else:
        path.unlink()
    return True, "removed"


def main() -> int:
    args = _parse_args()

    paths = _base_cleanup_paths()
    if args.include_caches:
        paths.extend(_cache_paths())

    total = 0
    removed = 0
    for path in _expand_paths(paths):
        total += 1
        changed, status = _remove_path(path, args.dry_run)
        if changed:
            removed += 1
            print(f"[{status}] {path}")

    action = "would be removed" if args.dry_run else "removed"
    print(f"Done: {removed} of {total} candidate paths {action}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
