"""Export dialog and worker for format-specific export operations."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from PySide6.QtCore import QThread, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QRadioButton,
    QVBoxLayout,
)

from wireviz_studio.core.exceptions import RenderError, WireVizStudioError
from wireviz_studio.export.csv_export import export_csv
from wireviz_studio.export.pdf_export import export_pdf
from wireviz_studio.export.png_export import export_png
from wireviz_studio.export.svg_export import export_svg


@dataclass
class ExportSelection:
    format_name: str
    output_path: str
    pdf_mode: str


class ExportWorker(QThread):
    progress = Signal(str)
    completed = Signal(str)
    failed = Signal(object)

    def __init__(self, selection: ExportSelection, svg_data: str, bom_rows: Iterable[dict]) -> None:
        super().__init__()
        self._selection = selection
        self._svg_data = svg_data
        self._bom_rows = list(bom_rows)

    def run(self) -> None:
        try:
            output_path = self._selection.output_path.strip()
            if not output_path:
                raise RenderError("Choose an output path before exporting.")

            target = self._normalized_path(output_path, self._selection.format_name)
            self.progress.emit(f"Exporting {self._selection.format_name}...")

            format_name = self._selection.format_name.upper()
            if format_name == "SVG":
                export_svg(self._svg_data, target)
            elif format_name == "PNG":
                export_png(self._svg_data, target)
            elif format_name == "CSV":
                export_csv(self._bom_rows, target)
            elif format_name == "PDF":
                export_pdf(self._svg_data, self._bom_rows, target, self._selection.pdf_mode)
            else:
                raise RenderError(f"Unsupported export format: {format_name}")

            self.completed.emit(target)
        except WireVizStudioError as exc:
            self.failed.emit(exc)
        except Exception as exc:
            self.failed.emit(RenderError(str(exc)))

    @staticmethod
    def _normalized_path(path_text: str, format_name: str) -> str:
        path = Path(path_text)
        if path.suffix:
            return str(path)

        suffix_map = {
            "PNG": ".png",
            "SVG": ".svg",
            "PDF": ".pdf",
            "CSV": ".csv",
        }
        return str(path.with_suffix(suffix_map.get(format_name.upper(), "")))


class ExportDialog(QDialog):
    def __init__(
        self,
        parent=None,
        default_path: str = "",
        default_format: str = "SVG",
        default_pdf_mode: str = "diagram",
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle("Export")
        self.resize(680, 360)

        self.format_combo = QComboBox(self)
        self.format_combo.addItems(["PNG", "SVG", "PDF", "CSV"])
        self.format_combo.setCurrentText(default_format.upper())

        self.path_edit = QLineEdit(default_path, self)
        browse_button = QPushButton("Browse", self)
        browse_button.clicked.connect(self._browse)

        path_row = QHBoxLayout()
        path_row.addWidget(self.path_edit)
        path_row.addWidget(browse_button)

        self.pdf_group = QGroupBox("PDF options", self)
        pdf_layout = QVBoxLayout(self.pdf_group)
        self.pdf_diagram = QRadioButton("Diagram only", self.pdf_group)
        self.pdf_bom = QRadioButton("BOM only", self.pdf_group)
        self.pdf_both = QRadioButton("Diagram + BOM", self.pdf_group)
        if default_pdf_mode == "bom":
            self.pdf_bom.setChecked(True)
        elif default_pdf_mode == "both":
            self.pdf_both.setChecked(True)
        else:
            self.pdf_diagram.setChecked(True)
        pdf_layout.addWidget(self.pdf_diagram)
        pdf_layout.addWidget(self.pdf_bom)
        pdf_layout.addWidget(self.pdf_both)

        form = QFormLayout()
        form.addRow("Format", self.format_combo)
        form.addRow("Output", path_row)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
            parent=self,
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        root = QVBoxLayout(self)
        root.addLayout(form)
        root.addWidget(self.pdf_group)
        root.addWidget(buttons)

        self.format_combo.currentTextChanged.connect(self._update_pdf_visibility)
        self._update_pdf_visibility(self.format_combo.currentText())

    def _browse(self) -> None:
        path, _ = QFileDialog.getSaveFileName(self, "Export output")
        if path:
            self.path_edit.setText(path)

    def _update_pdf_visibility(self, format_name: str) -> None:
        self.pdf_group.setVisible(format_name.upper() == "PDF")

    def selection(self) -> ExportSelection:
        if self.pdf_bom.isChecked():
            pdf_mode = "bom"
        elif self.pdf_both.isChecked():
            pdf_mode = "both"
        else:
            pdf_mode = "diagram"

        return ExportSelection(
            format_name=self.format_combo.currentText().upper(),
            output_path=self.path_edit.text().strip(),
            pdf_mode=pdf_mode,
        )
