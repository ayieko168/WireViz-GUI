# WireViz Studio

WireViz Studio is a cross-platform desktop application for creating wiring harness diagrams, connector pinout documentation, and bills of materials from WireViz-compatible YAML input.

It is designed for teams that want the clarity and version-control friendliness of a YAML-first workflow, but prefer a desktop editing, rendering, preview, and export experience over a CLI-only loop.

Created by [ayieko168](https://github.com/ayieko168).

## Credit to the Original WireViz Project

WireViz Studio explicitly credits the original [WireViz](https://github.com/wireviz/WireViz) project and its contributors.

WireViz established the YAML-driven approach for documenting cables, connectors, wiring harnesses, and BOMs with GraphViz-backed output. WireViz Studio builds on that foundation with a desktop workflow, while keeping the documentation and syntax model recognizable for users already familiar with WireViz.

WireViz Studio itself was created by [ayieko168](https://github.com/ayieko168), with the Studio application focusing on a richer desktop experience around that upstream-inspired workflow.

If you are looking for the upstream CLI-focused tool, original examples, or the canonical project history, refer to the original WireViz repository:

- https://github.com/wireviz/WireViz

It combines:

- A multi-tab YAML editor
- Manual YAML formatting with consistent indentation
- Manual render flow for fast, predictable iteration
- Diagram preview and BOM view
- Export to SVG, PNG, PDF, and CSV

## Why WireViz Studio

- Desktop-first workflow for editing and reviewing WireViz-compatible YAML
- Cross-platform GUI built with PySide6 for Windows, macOS, and Linux
- Built-in GraphViz detection with bundled fallback support
- Export pipeline for SVG, PNG, PDF, and CSV deliverables
- YAML-first source files that remain suitable for Git-based review and change tracking

## Interface Preview

![WireViz Studio main window showing YAML editing, harness diagram preview, and BOM output](screenshots/wireviz-studio.png)

## Key Features

- YAML-first workflow suitable for version control
- Cross-platform GUI built with PySide6
- Built-in GraphViz detection with bundled fallback support
- Automatic BOM generation from connector and cable definitions
- Syntax reference, examples, and tutorials aligned with the WireViz schema model
- Export worker pipeline with non-blocking UI execution
- Light and dark theme support

## Use Cases

- Wiring harness documentation for manufacturing or service teams
- Connector pinout references for bench testing and integration
- Cable assembly documentation with reproducible BOM output
- Desktop review of WireViz-style YAML before generating shareable artifacts

## Installation

### End Users

Download packaged builds from GitHub Releases:

- [Latest release page](https://github.com/ayieko168/wireviz-studio/releases/latest)

Direct package links for the current latest release `v1.0.1`:

- [Windows installer (.exe)](https://github.com/ayieko168/wireviz-studio/releases/download/v1.0.1/wireviz-studio-1.0.1-installer-windows-py3.13.exe)
- [Windows portable (.zip)](https://github.com/ayieko168/wireviz-studio/releases/download/v1.0.1/wireviz-studio-1.0.1-portable-windows-py3.13.zip)
- [macOS disk image (.dmg)](https://github.com/ayieko168/wireviz-studio/releases/download/v1.0.1/wireviz-studio-1.0.1-dmg-macos-py3.13.dmg)
- [macOS portable (.tar.gz)](https://github.com/ayieko168/wireviz-studio/releases/download/v1.0.1/wireviz-studio-1.0.1-portable-macos-py3.13.tar.gz)
- [Linux AppImage (.AppImage)](https://github.com/ayieko168/wireviz-studio/releases/download/v1.0.1/wireviz-studio-1.0.1-appimage-linux-py3.13.AppImage)
- [Linux portable (.tar.gz)](https://github.com/ayieko168/wireviz-studio/releases/download/v1.0.1/wireviz-studio-1.0.1-portable-linux-py3.13.tar.gz)

Release artifacts use explicit metadata in their filenames:

- `wireviz-studio-<version>-portable-<platform>-<python-tag>.<ext>`

### From Source

Requirements:

- Python 3.10+
- GraphViz available in PATH or bundled_graphviz location

Setup:

```powershell
./venv/Scripts/python.exe -m pip install --upgrade pip
./venv/Scripts/python.exe -m pip install ".[gui]"
```

Run the app:

```powershell
$env:PYTHONPATH = ".\src"
./venv/Scripts/python.exe -m wireviz_studio
```

## Quick Start

1. Open WireViz Studio.
2. Create a new YAML document.
3. Add connectors, cables, and connections.
4. Run Render.
5. Review diagram and BOM tabs.
6. Export to the required output format.

Minimal YAML example:

```yaml
connectors:
  X1:
    pincount: 2
  X2:
    pincount: 2

cables:
  W1:
    wirecount: 2
    length: 1

connections:
  - [X1, W1, X2]
```

## Documentation and Learning Path

Use the documentation in this order if you are new to the project:

1. Read the syntax reference in `syntax.md` to understand the YAML structure.
2. Walk through the guided examples in `../tutorial/readme.md`.
3. Browse the sample gallery in `../examples/readme.md`.
4. Use the desktop app to edit, render, validate, and export.

## Documentation Map

- Syntax reference: syntax.md
- Tutorial walkthrough: ../tutorial/readme.md
- Example gallery: ../examples/readme.md
- Advanced image usage: advanced_image_usage.md
- Contributor guide: CONTRIBUTING.md
- Changelog: CHANGELOG.md

## SEO-Friendly Project Summary

WireViz Studio is desktop software for YAML wiring diagrams, cable documentation, connector pinouts, and BOM export. It targets engineers and technical teams who need a practical GUI around the WireViz-style harness documentation workflow.

## Development and Packaging

Core tests:

```powershell
./venv/Scripts/python.exe -m pytest tests/core -q
```

Portable build:

```powershell
./venv/Scripts/python.exe packaging/build_portable.py --build-type portable --clean
```

Cleanup generated outputs:

```powershell
./venv/Scripts/python.exe packaging/clean_build_outputs.py --include-caches
```

## License

GPL-3.0-only
