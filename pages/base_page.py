"""Shared base class for all windows (code mode and .ui mode)."""
import html
import os

from PyQt6 import uic
from PyQt6.QtCore import QThread, Qt, pyqtSignal
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import (QFrame, QHBoxLayout, QLabel, QSplitter, QTableWidgetItem,
                             QTextEdit, QVBoxLayout, QWidget)

from styles import build_stylesheet

from paths import resource_dir

UI_DIR = os.path.join(resource_dir(), "ui")
LOGO_PATH = os.path.join(resource_dir(), "assets", "wearhere_logo.png")


def fill_table(table, headers, rows):
    """Replace the table content with the given headers and rows."""
    table.clear()
    table.setColumnCount(len(headers))
    table.setHorizontalHeaderLabels(headers)
    table.setRowCount(len(rows))
    for r, row in enumerate(rows):
        for c, value in enumerate(row):
            table.setItem(r, c, QTableWidgetItem(value))


def fill_detail(detail, table):
    """Show the selected row as readable text: one field per line, long values wrapped.

    The panel is hidden when no row is selected, so the table can use the full height.
    """
    row = table.currentRow()
    if row < 0:
        detail.clear()
        detail.hide()
        return
    lines = []
    for c in range(table.columnCount()):
        header = table.horizontalHeaderItem(c)
        name = header.text() if header else f"Column {c + 1}"
        item = table.item(row, c)
        value = item.text() if item else ""
        lines.append(f"<p style='margin:0 0 6px 0'><b>{html.escape(name)}:</b> "
                     f"{html.escape(value) or '-'}</p>")
    detail.setHtml("".join(lines))
    detail.show()


class SyncThread(QThread):
    """Runs the Drive sync in the background, so the window does not freeze."""
    done = pyqtSignal(str)

    def run(self):
        from data_store import sync_from_drive
        self.done.emit(sync_from_drive())


class BasePage(QWidget):
    navigate = pyqtSignal(str)  # name of the window to open
    message = pyqtSignal(str)   # text shown in the status bar
    UI_FILE = ""
    THEME = None
    LOGO_WIDTH = 0  # 0 = this page has no logo

    def __init__(self, use_ui_file=False):
        super().__init__()
        self.setObjectName("pageRoot")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)  # paint the stylesheet background
        self._sync_thread = None
        if use_ui_file:
            uic.loadUi(os.path.join(UI_DIR, self.UI_FILE), self)
        else:
            self.build_ui()
        self.setStyleSheet(build_stylesheet(self.THEME))
        self.apply_logo()
        self.connect_signals()

    def build_ui(self):
        raise NotImplementedError

    def apply_logo(self):
        label = getattr(self, "labelLogo", None)
        if label is None or not self.LOGO_WIDTH:
            return
        pixmap = QPixmap(LOGO_PATH).scaledToWidth(
            self.LOGO_WIDTH, Qt.TransformationMode.SmoothTransformation)
        label.setPixmap(pixmap)
        label.setFixedSize(pixmap.size())

    def connect_signals(self):
        pass

    def route(self, button, target):
        button.clicked.connect(lambda _checked=False, t=target: self.navigate.emit(t))

    def start_drive_refresh(self, button, after):
        """Start a Drive sync in the background; call after(status) when it ends."""
        if self._sync_thread is not None and self._sync_thread.isRunning():
            return
        self._after_sync = after
        self._refresh_button = button
        button.setEnabled(False)
        self.show_message("Refreshing from Drive...")
        self._sync_thread = SyncThread()
        self._sync_thread.done.connect(self._on_sync_done)
        self._sync_thread.start()

    def _on_sync_done(self, status):
        self._refresh_button.setEnabled(True)
        self._after_sync(status)

    def show_message(self, text):
        self.message.emit(text)

    def add_detail_panel(self, table):
        """Place a text panel under the table. Selecting a row fills it and shows it."""
        detail = QTextEdit()
        detail.setObjectName("detailText")
        detail.setReadOnly(True)
        detail.hide()
        layout = table.parentWidget().layout()
        index = layout.indexOf(table)
        layout.removeWidget(table)
        splitter = QSplitter(Qt.Orientation.Vertical)
        splitter.setChildrenCollapsible(False)
        splitter.addWidget(table)
        splitter.addWidget(detail)
        splitter.setSizes([480, 180])
        layout.insertWidget(index, splitter, 1)
        table.itemSelectionChanged.connect(lambda: fill_detail(detail, table))
        return detail

    def make_header(self, title, subtitle):
        bar = QFrame()
        bar.setObjectName("headerBar")
        layout = QVBoxLayout(bar)
        layout.setContentsMargins(24, 18, 24, 18)
        layout.setSpacing(2)
        title_label = QLabel(title)
        title_label.setObjectName("headerTitle")
        sub_label = QLabel(subtitle)
        sub_label.setObjectName("headerSub")
        layout.addWidget(title_label)
        layout.addWidget(sub_label)
        return bar

    def make_card(self):
        card = QFrame()
        card.setObjectName("card")
        return card

    def make_footer(self, *buttons):
        row = QHBoxLayout()
        row.addStretch()
        for button in buttons:
            row.addWidget(button)
        return row
