from PyQt6.QtWidgets import QHeaderView, QComboBox, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget, QVBoxLayout

from data_store import mentor_by_category, mentor_categories, search_rows
from pages.base_page import BasePage, fill_table
from styles import THEMES


HEADER_QSS = "QHeaderView::section { background-color: #22535F; color: #FFFFFF; font-weight: 700; font-size: 12px; padding: 10px 12px; border: none; border-right: 2px solid #C5E1E8; border-bottom: 3px solid #3F8FA0; }"


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



class MentorInterviewPage(BasePage):
    UI_FILE = "mentor_interview_page.ui"
    THEME = THEMES["mentor_interview"]

    def build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 24)
        root.setSpacing(16)
        root.addWidget(self.make_header("Mentor Interview", "Mentor conversations and sessions"))

        card = self.make_card()
        body = QVBoxLayout(card)
        body.setContentsMargins(20, 20, 20, 20)
        body.setSpacing(14)

        search_row = QHBoxLayout()
        self.inputSearch = QLineEdit()
        self.inputSearch.setPlaceholderText("Search conversations...")
        self.btnSearch = QPushButton("Search")
        search_row.addWidget(self.inputSearch, 1)
        search_row.addWidget(self.btnSearch)
        body.addLayout(search_row)

        filter_row = QHBoxLayout()
        self.labelFilter = QLabel("Tab")
        self.comboTabs = QComboBox()
        self.comboTabs.addItem("All Tabs")
        self.btnAllConversations = QPushButton("All Conversations")
        filter_row.addWidget(self.labelFilter)
        filter_row.addWidget(self.comboTabs, 1)
        filter_row.addWidget(self.btnAllConversations)
        body.addLayout(filter_row)

        self.tableConversations = QTableWidget(0, 0)
        self.tableConversations.setAlternatingRowColors(True)
        self.tableConversations.verticalHeader().setVisible(False)
        body.addWidget(self.tableConversations, 1)
        root.addWidget(card, 1)

        self.btnReturn = QPushButton("Return to Preferences Screen")
        root.addLayout(self.make_footer(self.btnReturn))

    def connect_signals(self):
        style_table(self.tableConversations)
        self.route(self.btnReturn, "return_preferences")
        self.current_category = None
        self.load_tabs()
        self.btnSearch.clicked.connect(self.refresh)
        self.inputSearch.returnPressed.connect(self.refresh)
        self.btnAllConversations.clicked.connect(self.show_all)
        self.comboTabs.currentIndexChanged.connect(self.on_tab_changed)

    def load_tabs(self):
        try:
            categories = mentor_categories()
        except (FileNotFoundError, ValueError) as error:
            categories = []
            self.show_message(str(error))
        self.comboTabs.blockSignals(True)
        self.comboTabs.clear()
        self.comboTabs.addItem("All Tabs")
        self.comboTabs.addItems(categories)
        self.comboTabs.blockSignals(False)

    def on_tab_changed(self, index):
        self.current_category = self.comboTabs.itemText(index) if index > 0 else None
        self.refresh()

    def show_all(self):
        self.comboTabs.blockSignals(True)
        self.comboTabs.setCurrentIndex(0)
        self.comboTabs.blockSignals(False)
        self.current_category = None
        self.refresh()

    def refresh(self, *_):
        try:
            headers, rows = mentor_by_category(self.current_category)
        except (FileNotFoundError, ValueError) as error:
            fill_table(self.tableConversations, [], [])
            self.show_message(str(error))
            return
        rows = search_rows(headers, rows, self.inputSearch.text())
        fill_table(self.tableConversations, headers, rows)
        self.show_message(f"{len(rows)} conversation(s) shown")
