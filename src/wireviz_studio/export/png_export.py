"""PNG export helpers."""

from __future__ import annotations

from PySide6.QtCore import QByteArray, QSize
from PySide6.QtGui import QColor, QImage, QPainter
from PySide6.QtSvg import QSvgRenderer

from wireviz_studio.core.exceptions import RenderError


def _safe_canvas_size(renderer: QSvgRenderer) -> QSize:
    size = renderer.defaultSize()
    if size.width() <= 0 or size.height() <= 0:
        return QSize(1600, 1000)
    return size


def export_png(svg_text: str, output_path: str) -> None:
    """Render SVG markup into PNG bytes on disk using Qt's SVG renderer."""
    renderer = QSvgRenderer(QByteArray(svg_text.encode("utf-8")))
    if not renderer.isValid():
        raise RenderError("Unable to export PNG: invalid SVG payload.")

    size = _safe_canvas_size(renderer)
    image = QImage(size, QImage.Format.Format_ARGB32)
    image.fill(QColor("#ffffff"))

    painter = QPainter(image)
    try:
        renderer.render(painter)
    finally:
        painter.end()

    if not image.save(output_path, "PNG"):
        raise RenderError(f"Unable to save PNG file: {output_path}")
