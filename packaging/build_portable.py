"""Build a portable WireViz Studio bundle with PyInstaller.

This script is intended for CI release jobs and writes a single compressed archive
under dist-artifacts/ for the current platform.
"""

from __future__ import annotations

import argparse
import platform
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST_ARTIFACTS = ROOT / "dist-artifacts"
APP_NAME = "WireVizStudio"


def _data_separator() -> str:
    return ";" if platform.system().lower().startswith("win") else ":"


def _platform_tag() -> str:
    system = platform.system().lower()
    if system.startswith("win"):
        return "windows"
    if system == "darwin":
        return "macos"
    return "linux"


def _python_tag() -> str:
    return f"py{sys.version_info.major}.{sys.version_info.minor}"


def _project_version() -> str:
    init_file = ROOT / "src" / "wireviz_studio" / "__init__.py"
    text = init_file.read_text(encoding="utf-8")
    match = re.search(r'__version__\s*=\s*"([^"]+)"', text)
    if not match:
        return "0.0.0"
    return match.group(1)


def _build_dirs(build_type: str) -> dict[str, Path]:
    base = ROOT / "build" / "packaging" / build_type / _platform_tag()
    return {
        "base": base,
        "spec": base / "spec",
        "work": base / "work",
        "dist": base / "dist",
    }


def _artifact_dir(build_type: str) -> Path:
    return DIST_ARTIFACTS / build_type / _platform_tag() / _python_tag()


def _remove_path(path: Path) -> None:
    if path.is_dir():
        shutil.rmtree(path)
    elif path.exists():
        path.unlink()


def _legacy_output_paths() -> list[Path]:
    legacy_artifacts = list(DIST_ARTIFACTS.glob("wireviz-studio-*"))
    return [
        ROOT / "dist",
        ROOT / f"{APP_NAME}.spec",
        ROOT / "build" / APP_NAME,
        *legacy_artifacts,
    ]


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build WireViz Studio portable package")
    parser.add_argument(
        "--build-type",
        default="portable",
        choices=["portable"],
        help="Build type label used in output folder and artifact names",
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Remove previous outputs for this build type/platform before building",
    )
    parser.add_argument(
        "--version",
        default="",
        help="Optional version override for artifact names (for example: v1.2.3)",
    )
    return parser.parse_args()


def _normalized_version(version_text: str) -> str:
    if not version_text:
        return _project_version()
    return version_text[1:] if version_text.startswith("v") else version_text


def _run_pyinstaller(build_type: str) -> Path:
    dirs = _build_dirs(build_type)
    sep = _data_separator()
    themes_src = ROOT / "src" / "wireviz_studio" / "gui" / "themes"
    add_data_args = [
        f"{themes_src}{sep}wireviz_studio/gui/themes",
    ]

    bundled_graphviz = ROOT / "bundled_graphviz"
    if bundled_graphviz.exists():
        add_data_args.append(f"{bundled_graphviz}{sep}bundled_graphviz")

    command = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--clean",
        "--onedir",
        "--windowed",
        "--name",
        APP_NAME,
        "--distpath",
        str(dirs["dist"]),
        "--workpath",
        str(dirs["work"]),
        "--specpath",
        str(dirs["spec"]),
        "--paths",
        "src",
        "--collect-submodules",
        "wireviz_studio",
    ]

    for add_data in add_data_args:
        command.extend(["--add-data", add_data])

    command.append("src/wireviz_studio/__main__.py")

    subprocess.run(command, check=True, cwd=ROOT)
    return dirs["dist"] / APP_NAME


def _make_archive(app_folder: Path, build_type: str, version_text: str) -> Path:
    artifact_dir = _artifact_dir(build_type)
    artifact_dir.mkdir(parents=True, exist_ok=True)

    if not app_folder.exists():
        raise FileNotFoundError(f"Expected app folder not found: {app_folder}")

    base_name = (
        "wireviz-studio-"
        f"{_normalized_version(version_text)}-"
        f"{build_type}-{_platform_tag()}-{_python_tag()}"
    )
    archive_base = artifact_dir / base_name

    if _platform_tag() == "windows":
        archive_path = shutil.make_archive(str(archive_base), "zip", root_dir=app_folder)
        return Path(archive_path)

    archive_path = shutil.make_archive(str(archive_base), "gztar", root_dir=app_folder)
    return Path(archive_path)


def main() -> int:
    args = _parse_args()
    dirs = _build_dirs(args.build_type)
    artifact_dir = _artifact_dir(args.build_type)

    if args.clean:
        for path in [dirs["base"], artifact_dir, *_legacy_output_paths()]:
            _remove_path(path)

    print(f"Build type     : {args.build_type}")
    print(f"Platform       : {_platform_tag()}")
    print(f"Python         : {_python_tag()}")
    print(f"Version        : {_normalized_version(args.version)}")
    print(f"PyInstaller out: {dirs['dist']}")
    print(f"Artifacts out  : {artifact_dir}")

    app_folder = _run_pyinstaller(args.build_type)
    archive = _make_archive(app_folder, args.build_type, args.version)
    print(f"Created artifact: {archive}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
