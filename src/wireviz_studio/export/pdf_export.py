"""PDF export helpers."""

from __future__ import annotations

import html
from typing import Iterable

from PySide6.QtCore import QByteArray, QRectF
from PySide6.QtGui import QPageLayout, QPageSize, QPainter, QPdfWriter, QTextDocument
from PySide6.QtSvg import QSvgRenderer

from wireviz_studio.core.exceptions import RenderError


def _render_diagram_page(painter: QPainter, writer: QPdfWriter, svg_text: str) -> None:
    renderer = QSvgRenderer(QByteArray(svg_text.encode("utf-8")))
    if not renderer.isValid():
        raise RenderError("Unable to export PDF diagram: invalid SVG payload.")

    page_rect = writer.pageLayout().paintRectPixels(writer.resolution())
    diagram_size = renderer.defaultSize()
    if diagram_size.width() <= 0 or diagram_size.height() <= 0:
        target = QRectF(page_rect)
    else:
        sx = page_rect.width() / diagram_size.width()
        sy = page_rect.height() / diagram_size.height()
        scale = min(sx, sy)
        target_w = diagram_size.width() * scale
        target_h = diagram_size.height() * scale
        x = page_rect.x() + (page_rect.width() - target_w) / 2
        y = page_rect.y() + (page_rect.height() - target_h) / 2
        target = QRectF(x, y, target_w, target_h)

    renderer.render(painter, target)


def _render_bom_page(painter: QPainter, writer: QPdfWriter, rows: Iterable[dict]) -> None:
    row_list = list(rows)
    headers = list(row_list[0].keys()) if row_list else []

    table_header = "".join(f"<th>{html.escape(str(col))}</th>" for col in headers)
    table_rows = []
    for row in row_list:
        cells = []
        for key in headers:
            value = row.get(key, "")
            if isinstance(value, list):
                value = ", ".join(str(item) for item in value)
            cells.append(f"<td>{html.escape(str(value))}</td>")
        table_rows.append(f"<tr>{''.join(cells)}</tr>")

    html_doc = f"""
    <html>
      <head>
        <style>
          body {{ font-family: 'Segoe UI', sans-serif; font-size: 10pt; }}
          h1 {{ font-size: 14pt; margin: 0 0 10px 0; }}
          table {{ border-collapse: collapse; width: 100%; }}
          th, td {{ border: 1px solid #333; padding: 4px; text-align: left; vertical-align: top; }}
          th {{ background: #efefef; }}
        </style>
      </head>
      <body>
        <h1>Bill of Materials</h1>
        <table>
          <thead><tr>{table_header}</tr></thead>
          <tbody>{''.join(table_rows)}</tbody>
        </table>
      </body>
    </html>
    """

    document = QTextDocument()
    document.setDocumentMargin(12.0)
    document.setHtml(html_doc)

    page_rect = writer.pageLayout().paintRectPixels(writer.resolution())
    document.setPageSize(page_rect.size())
    painter.save()
    painter.translate(page_rect.x(), page_rect.y())
    document.drawContents(painter, QRectF(0, 0, page_rect.width(), page_rect.height()))
    painter.restore()


def export_pdf(svg_text: str, rows: Iterable[dict], output_path: str, pdf_mode: str) -> None:
    """Export PDF for diagram, BOM, or both pages."""
    writer = QPdfWriter(output_path)
    writer.setPageSize(QPageSize(QPageSize.PageSizeId.A4))
    writer.setPageOrientation(QPageLayout.Orientation.Landscape)
    writer.setResolution(300)
    writer.setTitle("WireViz Studio Export")
    writer.setCreator("WireViz Studio")

    painter = QPainter(writer)
    if not painter.isActive():
        raise RenderError(f"Unable to open PDF for writing: {output_path}")

    try:
        mode = pdf_mode.lower()
        if mode == "diagram":
            _render_diagram_page(painter, writer, svg_text)
        elif mode == "bom":
            _render_bom_page(painter, writer, rows)
        elif mode == "both":
            _render_diagram_page(painter, writer, svg_text)
            writer.newPage()
            _render_bom_page(painter, writer, rows)
        else:
            raise RenderError(f"Unsupported PDF mode: {pdf_mode}")
    finally:
        painter.end()
