"""Diagram/BOM preview widgets."""

from __future__ import annotations

from typing import Iterable

from PySide6.QtCore import QByteArray, Qt
from PySide6.QtGui import QAction, QColor, QBrush, QKeySequence, QPainter
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtSvgWidgets import QGraphicsSvgItem
from PySide6.QtWidgets import (
	QApplication,
	QGraphicsScene,
	QGraphicsView,
	QHeaderView,
	QMenu,
	QPushButton,
	QStyle,
	QTableWidget,
	QTableWidgetItem,
	QTabWidget,
	QToolButton,
	QVBoxLayout,
	QWidget,
)


class DiagramView(QGraphicsView):
	def __init__(self, parent=None) -> None:
		super().__init__(parent)
		self.setScene(QGraphicsScene(self))
		self.setCacheMode(QGraphicsView.CacheModeFlag.CacheBackground)
		self.setRenderHints(QPainter.RenderHint.Antialiasing | QPainter.RenderHint.SmoothPixmapTransform)
		self.setOptimizationFlag(QGraphicsView.OptimizationFlag.DontSavePainterState, True)
		self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
		self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorViewCenter)
		self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
		self.setBackgroundBrush(QBrush(QColor("#ffffff")))
		self._zoom = 1.0
		self._svg_renderer: QSvgRenderer | None = None

	def wheelEvent(self, event) -> None:
		factor = 1.15 if event.angleDelta().y() > 0 else 1 / 1.15
		self.scale(factor, factor)
		self._zoom *= factor

	def fit_diagram(self) -> None:
		if self.scene() and self.scene().items():
			self.fitInView(self.scene().itemsBoundingRect(), Qt.AspectRatioMode.KeepAspectRatio)
			self._zoom = 1.0

	def set_svg(self, svg_text: str) -> None:
		scene = self.scene()
		scene.clear()
		renderer = QSvgRenderer(QByteArray(svg_text.encode("utf-8")), self)
		self._svg_renderer = renderer
		svg_item = QGraphicsSvgItem()
		svg_item.setSharedRenderer(renderer)
		scene.addItem(svg_item)
		self.fit_diagram()


class BomTableWidget(QTableWidget):
	def __init__(self, parent=None) -> None:
		super().__init__(parent)
		self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
		self.customContextMenuRequested.connect(self._show_context_menu)

	def _show_context_menu(self, position) -> None:
		menu = QMenu(self)
		copy_action = QAction("Copy", self)
		copy_action.setShortcut(QKeySequence.StandardKey.Copy)
		copy_action.triggered.connect(self.copy_selected_cells)
		menu.addAction(copy_action)
		menu.exec(self.viewport().mapToGlobal(position))

	def keyPressEvent(self, event) -> None:
		if event.matches(QKeySequence.StandardKey.Copy):
			self.copy_selected_cells()
			event.accept()
			return
		super().keyPressEvent(event)

	def copy_selected_cells(self) -> None:
		ranges = self.selectedRanges()
		if not ranges:
			self.selectAll()
			ranges = self.selectedRanges()
			if not ranges:
				return

		cell_range = ranges[0]
		lines = []
		for row in range(cell_range.topRow(), cell_range.bottomRow() + 1):
			row_values = []
			for col in range(cell_range.leftColumn(), cell_range.rightColumn() + 1):
				item = self.item(row, col)
				row_values.append(item.text() if item else "")
			lines.append("\t".join(row_values))

		if lines:
			QApplication.clipboard().setText("\n".join(lines))
		self.clearSelection()


class PreviewPanel(QWidget):
	def __init__(self, parent=None) -> None:
		super().__init__(parent)

		self.tabs = QTabWidget(self)
		self.tabs.setObjectName("preview_tabs")

		self.diagram_view = DiagramView(self)
		self.fit_button = QToolButton(self)
		self.fit_button.setText("Fit")
		self.fit_button.setToolTip("Fit diagram to view")
		self.fit_button.setFixedSize(50, 28)
		self.fit_button.clicked.connect(self.diagram_view.fit_diagram)
		diagram_container = QWidget(self)
		diagram_layout = QVBoxLayout(diagram_container)
		diagram_layout.setContentsMargins(0, 0, 0, 0)
		diagram_layout.addWidget(self.diagram_view)
		diagram_layout.addWidget(self.fit_button, alignment=Qt.AlignmentFlag.AlignRight)

		self.bom_table = BomTableWidget(self)
		self.bom_table.setObjectName("bom_table")
		self.bom_table.setSortingEnabled(True)
		self.bom_table.setAlternatingRowColors(True)
		self.bom_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
		self.bom_table.horizontalHeader().setStretchLastSection(False)
		self.bom_table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

		self.tabs.addTab(diagram_container, "Diagram")
		self.tabs.addTab(self.bom_table, "BOM")

		layout = QVBoxLayout(self)
		layout.setContentsMargins(0, 0, 0, 0)
		layout.addWidget(self.tabs)

	def set_svg(self, svg_text: str) -> None:
		self.diagram_view.set_svg(svg_text)

	def set_bom(self, rows: Iterable[dict]) -> None:
		rows = list(rows)
		if not rows:
			self.bom_table.clear()
			self.bom_table.setRowCount(0)
			self.bom_table.setColumnCount(0)
			return

		self.bom_table.setSortingEnabled(False)
		columns = list(rows[0].keys())
		self.bom_table.setColumnCount(len(columns))
		self.bom_table.setHorizontalHeaderLabels(columns)
		self.bom_table.setRowCount(len(rows))

		for row_index, row in enumerate(rows):
			for column_index, column_name in enumerate(columns):
				value = row.get(column_name, "")
				if isinstance(value, list):
					value = ", ".join(str(item) for item in value)
				item = QTableWidgetItem(str(value))
				self.bom_table.setItem(row_index, column_index, item)
		self.bom_table.setSortingEnabled(True)
