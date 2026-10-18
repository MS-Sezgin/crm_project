"""Navigation, data and Google-mock smoke test, run for both code mode and .ui mode.

Run:  python test_navigation.py
Uses temporary sample files, so your data/ and credentials/ folders are not touched.
Google calls are replaced with fake functions here.
"""
import os
import sys
import tempfile

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
DATA_DIR = tempfile.mkdtemp(prefix="crm_test_")
os.environ["CRM_DATA_DIR"] = DATA_DIR
os.environ["CRM_CREDENTIALS_DIR"] = tempfile.mkdtemp(prefix="crm_creds_")

from openpyxl import Workbook  # noqa: E402
from PyQt6.QtWidgets import QApplication  # noqa: E402

import google_services  # noqa: E402
from main import MainWindow  # noqa: E402


def write_sheet(name, header, rows):
    wb = Workbook()
    ws = wb.active
    ws.append(header)
    for row in rows:
        ws.append(list(row))
    wb.save(os.path.join(DATA_DIR, name))


write_sheet("Users.xlsx", ["Username", "Password", "Role"],
            [("student", "1234", "User"), ("admin", "admin", "Admin")])
write_sheet("Applications.xlsx", ["Name Surname", "Mail", "Mentor Meeting"],
            [("Ali As", "a@x.com", "Yes"), ("Asli Kaya", "b@x.com", ""), ("Mehmet Demir", "c@x.com", "Yes"),
             ("Ali As", "a@x.com", "")])
write_sheet("VIT1.xlsx", ["Name Surname", "Mail"],
            [("Ali As", "a@x.com"), ("Asli Kaya", "b@x.com"), ("Zeynep Can", "z@x.com")])
write_sheet("VIT2.xlsx", ["Name Surname", "Mail"],
            [("Ali As", "a@x.com"), ("Mehmet Demir", "c@x.com")])
write_sheet("Interviews.xlsx", ["Adiniz Soyadiniz", "Proje gonderilis tarihi", "Projenin gelis tarihi"],
            [("Ali As", "13.06.2023", "07.08.2023"), ("Ayse Yildiz", "18.06.2023", None)])
write_sheet("Mentor.xlsx", ["Date", "Candidate Name", "Recommendation"],
            [("05.05.2023", "Zeynep Yilmaz", "Mentor Meetings"), ("10.05.2023", "Ahmet Can", "Follow-up")])

FAKE_EVENTS = [
    {"name": "Mentor Kickoff", "start": "20.10.2026 10:00", "participants": ["p1@x.com", "p2@x.com"], "organizer": "org@x.com"},
    {"name": "Interview Day", "start": "22.10.2026 14:00", "participants": [], "organizer": "org@x.com"},
]
SENT = []
google_services.fetch_events = lambda *a, **k: list(FAKE_EVENTS)
google_services.send_email = lambda to, subject, body: SENT.append((list(to), subject))


def check(condition, message):
    if not condition:
        raise AssertionError(message)


def run_flow(use_ui_file):
    app = QApplication.instance() or QApplication(sys.argv)
    check(app is not None, "QApplication must exist")
    win = MainWindow(use_ui_file=use_ui_file)
    pages = win.pages
    login = pages["login"]

    def current():
        return win.stack.currentWidget()

    login.inputUsername.setText("student")
    login.inputPassword.setText("wrong")
    login.btnLogin.click()
    check(current() is pages["login"], "wrong password should not navigate")
    check("Incorrect" in login.labelWarning.text(), "wrong password should show a warning")

    login.inputUsername.setText("student")
    login.inputPassword.setText("1234")
    login.btnLogin.click()
    check(current() is pages["preferences"], "user should reach Preferences")
    pages["preferences"].btnLogout.click()
    check(current() is pages["login"], "log out should return to login")
    check(login.inputUsername.text() == "", "log out should clear the login form")
    login.inputUsername.setText("student")
    login.inputPassword.setText("1234")
    login.btnLogin.click()
    check(current() is pages["preferences"], "user should log in again after log out")

    pages["preferences"].btnApplications.click()
    apps = pages["applications"]
    apps.btnAllApplications.click()
    check(apps.tableApplications.rowCount() == 4, "All Applications should show 4 rows")
    apps.btnMeetingDefined.click()
    check(apps.tableApplications.rowCount() == 2, "Mentor Meeting Defined should show 2 rows")
    apps.btnMeetingNotDefined.click()
    check(apps.tableApplications.rowCount() == 2, "Mentor Meeting Not Defined should show 2 rows")
    apps.btnAllApplications.click()
    apps.inputSearch.setText("as")
    apps.btnSearch.click()
    check(apps.tableApplications.rowCount() == 3, "search 'as' should find 3 rows")
    apps.inputSearch.setText("")
    apps.comboFilters.setCurrentIndex(1)  # Duplicate Records
    check(apps.tableApplications.rowCount() == 2, "duplicates should show 2 rows")
    apps.comboFilters.setCurrentIndex(2)  # Previous VIT Check
    check(apps.tableApplications.rowCount() == 3, "previous VIT check should show 3 people")
    apps.comboFilters.setCurrentIndex(3)  # Different Record
    check(apps.tableApplications.rowCount() == 3, "different record should show 3 people")
    apps.comboFilters.setCurrentIndex(4)  # Application Filter
    check(apps.tableApplications.rowCount() == 3, "application filter should show each name once")
    apps.inputSearch.setText("")
    apps.btnReturn.click()
    check(current() is pages["preferences"], "Applications return failed")

    pages["preferences"].btnInterviews.click()
    iv = pages["interviews"]
    iv.btnProjectSent.click()
    check(iv.tableInterviews.rowCount() == 2, "Project Sent should show 2 rows")
    iv.btnProjectReceived.click()
    check(iv.tableInterviews.rowCount() == 1, "Project Received should show 1 row")
    iv.btnReturn.click()

    pages["preferences"].btnMentorInterview.click()
    mt = pages["mentor_interview"]
    check(mt.comboTabs.count() == 3, "tab combo should have All Tabs + 2 categories")
    mt.btnAllConversations.click()
    check(mt.tableConversations.rowCount() == 2, "All Conversations should show 2 rows")
    mt.comboTabs.setCurrentIndex(1)
    check(mt.tableConversations.rowCount() == 1, "category filter should show 1 row")
    mt.btnReturn.click()

    # Admin with mocked Google
    login.inputUsername.setText("admin")
    login.inputPassword.setText("admin")
    win.show_page("login")
    login.btnLogin.click()
    check(current() is pages["preferences_admin"], "admin should reach admin Preferences")
    pages["preferences_admin"].btnAdmin.click()
    adm = pages["admin_menu"]
    check(current() is adm, "Admin Menu not opened")

    adm.btnEventRecord.click()
    check(adm.tableCalendar.columnCount() == 4, "Admin table should have 4 columns")
    check(adm.tableCalendar.rowCount() == 2, "Event Record should show 2 events")

    adm.tableCalendar.selectRow(1)  # event without participants
    before = len(SENT)
    adm.confirm = lambda text: True
    adm.btnMail.click()
    check(len(SENT) == before, "event without participants must not send mail")

    adm.tableCalendar.selectRow(0)
    adm.confirm = lambda text: False
    adm.btnMail.click()
    check(len(SENT) == before, "cancelled confirmation must not send mail")

    adm.confirm = lambda text: True
    adm.btnMail.click()
    check(len(SENT) == before + 1, "confirmed mail should be sent once")
    check(SENT[-1][0] == ["p1@x.com", "p2@x.com"], "mail should go to the event participants")

    adm.btnReturnAdmin.click()
    check(current() is pages["preferences_admin"], "Admin Menu return failed")
    pages["preferences_admin"].btnApplications.click()
    pages["applications"].btnReturn.click()
    check(current() is pages["preferences_admin"], "admin return should go to admin Preferences")

    win.close()
    print(f"[{'UI files' if use_ui_file else 'code'}] all checks OK")


def run_drive_checks():
    import data_store
    google_services.sync_drive_files = lambda target, names: {"Users.xlsx": "downloaded", "VIT1.xlsx": "not found"}
    check("1 file(s) updated" in data_store.sync_from_drive(), "updated files should be reported")

    google_services.sync_drive_files = lambda target, names: {n: "up to date" for n in names}
    check("up to date" in data_store.sync_from_drive(), "unchanged files should be reported as up to date")

    def offline(target, names):
        raise OSError("no internet")
    google_services.sync_drive_files = offline
    check("using local files" in data_store.sync_from_drive(), "offline start should fall back to local files")
    print("[Drive sync] checks OK")


if __name__ == "__main__":
    run_flow(False)
    run_flow(True)
    run_drive_checks()
    print("All checks passed.")
