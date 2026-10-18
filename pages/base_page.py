"""Shared base class for all windows (code mode and .ui mode)."""
import os

from PyQt6 import uic
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel, QTableWidgetItem, QVBoxLayout, QWidget

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


class BasePage(QWidget):
    navigate = pyqtSignal(str)  # name of the window to open
    message = pyqtSignal(str)   # text shown in the status bar
    UI_FILE = ""
    THEME = None
    LOGO_WIDTH = 0  # 0 = this page has no logo

    def __init__(self, use_ui_file=False):
        super().__init__()
        self.setObjectName("pageRoot")
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

    def show_message(self, text):
        self.message.emit(text)

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
