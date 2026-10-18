"""CRM Capstone (Excel-based version).

Run:
    python main.py        -> pages built in Python code (.py versions)
    python main.py --ui   -> pages loaded from the Qt Designer files in ui/
"""
import sys

from PyQt6.QtWidgets import QApplication, QMainWindow, QStackedWidget

from data_store import sync_from_drive
from pages.login_page import LoginPage
from pages.preferences_page import PreferencesPage
from pages.preferences_admin_page import PreferencesAdminPage
from pages.applications_page import ApplicationsPage
from pages.mentor_interview_page import MentorInterviewPage
from pages.interviews_page import InterviewsPage
from pages.admin_menu_page import AdminMenuPage


class MainWindow(QMainWindow):
    def __init__(self, use_ui_file=False):
        super().__init__()
        self.setWindowTitle("CRM Capstone")
        self.resize(1100, 780)
        self.setMinimumSize(820, 600)
        self.is_admin = False

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.pages = {
            "login": LoginPage(use_ui_file),
            "preferences": PreferencesPage(use_ui_file),
            "preferences_admin": PreferencesAdminPage(use_ui_file),
            "applications": ApplicationsPage(use_ui_file),
            "mentor_interview": MentorInterviewPage(use_ui_file),
            "interviews": InterviewsPage(use_ui_file),
            "admin_menu": AdminMenuPage(use_ui_file),
        }
        for page in self.pages.values():
            page.navigate.connect(self.handle_navigation)
            page.message.connect(self.statusBar().showMessage)
            self.stack.addWidget(page)

        self.show_page("login")

    def closeEvent(self, event):
        """Wait for a running Drive download, so a file is never left half-written."""
        for page in self.pages.values():
            thread = page._sync_thread
            if thread is not None and thread.isRunning():
                self.statusBar().showMessage("Waiting for the Drive download to finish...")
                QApplication.processEvents()
                thread.wait()
        event.accept()

    def show_page(self, name):
        self.stack.setCurrentWidget(self.pages[name])

    def handle_navigation(self, target):
        if target == "exit":
            self.close()  # goes through closeEvent, so a running Drive download is finished first
            return
        if target == "return_preferences":
            target = "preferences_admin" if self.is_admin else "preferences"
        if target == "preferences":
            self.is_admin = False
        elif target == "preferences_admin":
            self.is_admin = True
        if target == "login":
            self.is_admin = False
            self.pages["login"].reset()
        self.show_page(target)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    sync_status = sync_from_drive()
    window = MainWindow(use_ui_file="--ui" in sys.argv)
    window.showMaximized()
    window.statusBar().showMessage(sync_status)
    sys.exit(app.exec())
