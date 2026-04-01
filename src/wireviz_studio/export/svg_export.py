"""SVG export helpers."""

from __future__ import annotations

from pathlib import Path


def export_svg(svg_text: str, output_path: str) -> None:
    """Write rendered SVG markup to disk."""
    Path(output_path).write_text(svg_text, encoding="utf-8")
