from PyQt6.QtWidgets import (QHeaderView, QComboBox, QHBoxLayout, QLabel, QLineEdit, QPushButton,
                             QTableWidget, QVBoxLayout)

from data_store import (APPLICATIONS_FILE, applications_by_mentor, different_records,
                        duplicate_applications, load_sheet, people_as_table, previous_vit_check,
                        search_rows, unique_applications)
from pages.base_page import BasePage, fill_table
from styles import THEMES

EXTRA_FILTERS = [
    ("More filters...", None),
    ("Duplicate Records", "duplicates"),
    ("Previous VIT Check", "previous_vit"),
    ("Different Record", "different"),
    ("Application Filter", "unique"),
]


HEADER_QSS = "QHeaderView::section { background-color: #4B3F72; color: #FFFFFF; font-weight: 700; font-size: 12px; padding: 10px 12px; border: none; border-right: 2px solid #D8D2EC; border-bottom: 3px solid #6E5EA8; }"


def style_table(table):
    """Make header labels readable: fixed default width, wrapped text, no clipping."""
    header = table.horizontalHeader()
    header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
    header.setDefaultSectionSize(180)
    header.setMinimumSectionSize(130)
    header.setStretchLastSection(False)
    header.setHighlightSections(False)
    header.setMinimumHeight(44)
    table.setStyleSheet(HEADER_QSS)



class ApplicationsPage(BasePage):
    UI_FILE = "applications_page.ui"
    THEME = THEMES["applications"]

    def build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 24)
        root.setSpacing(16)
        root.addWidget(self.make_header("Applications", "Search and review submitted applications"))

        card = self.make_card()
        body = QVBoxLayout(card)
        body.setContentsMargins(20, 20, 20, 20)
        body.setSpacing(14)

        search_row = QHBoxLayout()
        self.inputSearch = QLineEdit()
        self.inputSearch.setPlaceholderText("Search applications...")
        self.btnSearch = QPushButton("Search")
        search_row.addWidget(self.inputSearch, 1)
        search_row.addWidget(self.btnSearch)
        body.addLayout(search_row)

        filter_row = QHBoxLayout()
        self.btnAllApplications = QPushButton("All Applications")
        self.btnMeetingDefined = QPushButton("Mentor Meeting Defined")
        self.btnMeetingNotDefined = QPushButton("Mentor Meeting Not Defined")
        for button in (self.btnAllApplications, self.btnMeetingDefined, self.btnMeetingNotDefined):
            filter_row.addWidget(button)
        body.addLayout(filter_row)

        combo_row = QHBoxLayout()
        self.labelFilter = QLabel("Filter")
        self.comboFilters = QComboBox()
        self.comboFilters.addItems([label for label, _ in EXTRA_FILTERS])
        combo_row.addWidget(self.labelFilter)
        combo_row.addWidget(self.comboFilters, 1)
        body.addLayout(combo_row)

        self.tableApplications = QTableWidget(0, 0)
        self.tableApplications.setAlternatingRowColors(True)
        self.tableApplications.verticalHeader().setVisible(False)
        body.addWidget(self.tableApplications, 1)
        root.addWidget(card, 1)

        self.btnRefresh = QPushButton("Refresh")
        self.btnReturn = QPushButton("Return to Preferences Screen")
        self.btnExit = QPushButton("Exit")
        self.btnExit.setObjectName("btnExit")
        root.addLayout(self.make_footer(self.btnRefresh, self.btnReturn, self.btnExit))

    def connect_signals(self):
        style_table(self.tableApplications)
        self.route(self.btnReturn, "return_preferences")
        self.btnRefresh.clicked.connect(self.on_refresh)
        self.route(self.btnExit, "exit")
        self.current_view = "all"
        self.btnSearch.clicked.connect(self.refresh)
        self.inputSearch.returnPressed.connect(self.refresh)
        self.btnAllApplications.clicked.connect(lambda: self.set_view("all"))
        self.btnMeetingDefined.clicked.connect(lambda: self.set_view("defined"))
        self.btnMeetingNotDefined.clicked.connect(lambda: self.set_view("not_defined"))
        self.comboFilters.currentIndexChanged.connect(self.on_extra_filter)

    def on_extra_filter(self, index):
        view = EXTRA_FILTERS[index][1]
        if view:
            self.set_view(view)

    def set_view(self, view):
        self.current_view = view
        self.refresh()

    def load_view(self):
        view = self.current_view
        if view == "all":
            return load_sheet(APPLICATIONS_FILE)
        if view in ("defined", "not_defined"):
            return applications_by_mentor(defined=view == "defined")
        if view == "duplicates":
            return duplicate_applications()
        if view == "unique":
            return unique_applications()
        if view == "previous_vit":
            return people_as_table(previous_vit_check())
        if view == "different":
            return people_as_table(different_records())
        return load_sheet(APPLICATIONS_FILE)

    def on_refresh(self, *_):
        self.start_drive_refresh(self.btnRefresh, self.finish_refresh)

    def finish_refresh(self, status):
        text = self.refresh()
        self.show_message(f"{status}. {text}" if text else status)

    def refresh(self, *_):
        try:
            headers, rows = self.load_view()
        except (FileNotFoundError, ValueError) as error:
            fill_table(self.tableApplications, [], [])
            self.show_message(str(error))
            return
        rows = search_rows(headers, rows, self.inputSearch.text())
        fill_table(self.tableApplications, headers, rows)
        message = f"{len(rows)} record(s) shown"
        self.show_message(message)
        return message
