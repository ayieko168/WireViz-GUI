"""Bundled GraphViz binary detection utilities."""

from __future__ import annotations

import os
import platform
from pathlib import Path
from typing import Optional


def platform_bundle_dir() -> str:
	"""Return bundled platform directory name used under bundled_graphviz/."""
	system_name = platform.system().lower()
	if system_name.startswith("win"):
		return "windows"
	if system_name == "darwin":
		return "macos"
	return "linux"


def dot_name() -> str:
	"""Return platform-specific dot executable name."""
	return "dot.exe" if platform.system().lower().startswith("win") else "dot"


def _default_repo_root() -> Path:
	# src/wireviz_studio/graphviz_manager/bundled.py -> repo root is parents[3]
	return Path(__file__).resolve().parents[3]


def find_bundled_dot(app_root: Optional[Path] = None) -> Optional[Path]:
	"""Find a bundled dot executable for the current platform.

	Layout expected by plan:
	bundled_graphviz/<platform>/<version-or-folder>/bin/dot(.exe)
	"""
	repo_root = Path(app_root) if app_root else _default_repo_root()
	platform_root = repo_root / "bundled_graphviz" / platform_bundle_dir()
	if not platform_root.exists():
		return None

	executable_name = dot_name()

	direct_bin = platform_root / "bin" / executable_name
	if direct_bin.exists():
		return direct_bin.resolve()

	candidates = []
	for child_dir in platform_root.iterdir():
		if not child_dir.is_dir():
			continue
		candidate = child_dir / "bin" / executable_name
		if candidate.exists():
			candidates.append(candidate.resolve())

	if not candidates:
		return None

	# Prefer lexicographically latest folder/version naming.
	return sorted(candidates)[-1]


def configure_bundled_dot(app_root: Optional[Path] = None) -> Optional[Path]:
	"""Set environment for bundled dot and return executable path when available."""
	dot_path = find_bundled_dot(app_root=app_root)
	if not dot_path:
		return None

	os.environ["GRAPHVIZ_DOT"] = str(dot_path)

	dot_dir = str(dot_path.parent)
	current_path = os.environ.get("PATH", "")
	path_entries = current_path.split(os.pathsep) if current_path else []
	if dot_dir not in path_entries:
		os.environ["PATH"] = dot_dir + (os.pathsep + current_path if current_path else "")

	return dot_path
