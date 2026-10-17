from PyQt6.QtWidgets import QHeaderView, QHBoxLayout, QLineEdit, QPushButton, QTableWidget, QVBoxLayout

from data_store import interviews_by_status, search_rows
from pages.base_page import BasePage, fill_table
from styles import THEMES


HEADER_QSS = "QHeaderView::section { background-color: #46521F; color: #FFFFFF; font-weight: 700; font-size: 12px; padding: 10px 12px; border: none; border-right: 2px solid #DCE5C4; border-bottom: 3px solid #7D8F45; }"


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



class InterviewsPage(BasePage):
    UI_FILE = "interviews_page.ui"
    THEME = THEMES["interviews"]

    def build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 24)
        root.setSpacing(16)
        root.addWidget(self.make_header("Interviews", "Project exchange between students and mentors"))

        card = self.make_card()
        body = QVBoxLayout(card)
        body.setContentsMargins(20, 20, 20, 20)
        body.setSpacing(14)

        search_row = QHBoxLayout()
        self.inputSearch = QLineEdit()
        self.inputSearch.setPlaceholderText("Search interviews...")
        self.btnSearch = QPushButton("Search")
        search_row.addWidget(self.inputSearch, 1)
        search_row.addWidget(self.btnSearch)
        body.addLayout(search_row)

        button_row = QHBoxLayout()
        self.btnProjectSent = QPushButton("Project Sent")
        self.btnProjectReceived = QPushButton("Project Received")
        button_row.addWidget(self.btnProjectSent)
        button_row.addWidget(self.btnProjectReceived)
        body.addLayout(button_row)

        self.tableInterviews = QTableWidget(0, 0)
        self.tableInterviews.setAlternatingRowColors(True)
        self.tableInterviews.verticalHeader().setVisible(False)
        body.addWidget(self.tableInterviews, 1)
        root.addWidget(card, 1)

        self.btnReturn = QPushButton("Return to Preferences Screen")
        root.addLayout(self.make_footer(self.btnReturn))

    def connect_signals(self):
        style_table(self.tableInterviews)
        self.route(self.btnReturn, "return_preferences")
        self.current_view = None
        self.btnSearch.clicked.connect(self.refresh)
        self.inputSearch.returnPressed.connect(self.refresh)
        self.btnProjectSent.clicked.connect(lambda: self.set_view("sent"))
        self.btnProjectReceived.clicked.connect(lambda: self.set_view("received"))

    def set_view(self, view):
        self.current_view = view
        self.refresh()

    def refresh(self, *_):
        try:
            headers, rows = interviews_by_status(self.current_view)
        except (FileNotFoundError, ValueError) as error:
            fill_table(self.tableInterviews, [], [])
            self.show_message(str(error))
            return
        rows = search_rows(headers, rows, self.inputSearch.text())
        fill_table(self.tableInterviews, headers, rows)
        self.show_message(f"{len(rows)} interview record(s) shown")
