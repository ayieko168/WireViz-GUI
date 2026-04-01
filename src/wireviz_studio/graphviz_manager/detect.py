"""System GraphViz detection and verification utilities."""

from __future__ import annotations

import os
import platform
import shutil
import subprocess
from pathlib import Path
from typing import Optional


def _subprocess_windows_flags() -> int:
	if platform.system().lower().startswith("win"):
		return getattr(subprocess, "CREATE_NO_WINDOW", 0)
	return 0


def verify_dot(dot_path: Path) -> bool:
	"""Return True when executable responds successfully to `dot -V`."""
	try:
		completed = subprocess.run(
			[str(dot_path), "-V"],
			capture_output=True,
			text=True,
			timeout=5,
			check=False,
			creationflags=_subprocess_windows_flags(),
		)
		return completed.returncode == 0 and "graphviz" in (
			(completed.stderr or "") + (completed.stdout or "")
		).lower()
	except (OSError, subprocess.SubprocessError):
		return False


def dot_version(dot_path: Path) -> Optional[str]:
	"""Return a version string from `dot -V` output when available."""
	try:
		completed = subprocess.run(
			[str(dot_path), "-V"],
			capture_output=True,
			text=True,
			timeout=5,
			check=False,
			creationflags=_subprocess_windows_flags(),
		)
	except (OSError, subprocess.SubprocessError):
		return None

	output_text = ((completed.stderr or "") + "\n" + (completed.stdout or "")).strip()
	if not output_text:
		return None

	first_line = output_text.splitlines()[0].strip()
	return first_line if first_line else None


def _windows_common_dot_locations() -> list[Path]:
	return [
		Path(r"C:\Program Files\Graphviz\bin\dot.exe"),
		Path(r"C:\Program Files (x86)\Graphviz\bin\dot.exe"),
	]


def find_system_dot() -> Optional[Path]:
	"""Find system-installed dot executable from PATH and common locations."""
	which_result = shutil.which("dot")
	if which_result:
		dot_path = Path(which_result).resolve()
		if verify_dot(dot_path):
			return dot_path

	if platform.system().lower().startswith("win"):
		for candidate in _windows_common_dot_locations():
			if candidate.exists() and verify_dot(candidate):
				return candidate.resolve()

	return None


def configure_system_dot() -> Optional[Path]:
	"""Set environment for system dot and return executable path when found."""
	dot_path = find_system_dot()
	if not dot_path:
		return None

	os.environ["GRAPHVIZ_DOT"] = str(dot_path)
	dot_dir = str(dot_path.parent)
	current_path = os.environ.get("PATH", "")
	path_entries = current_path.split(os.pathsep) if current_path else []
	if dot_dir not in path_entries:
		os.environ["PATH"] = dot_dir + (os.pathsep + current_path if current_path else "")
	return dot_path
