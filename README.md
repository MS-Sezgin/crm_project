# CRM Capstone

A desktop CRM application built with PyQt6. It manages refugee IT candidates: applications, mentor meetings, project interviews and calendar-based reminders.

## Features

- **Login** with role check (Admin / User) from `Users.xlsx`
- **Applications**: all, mentor meeting defined / not defined, name search, and filters for duplicate records, unique names, previous VIT check and different records
- **Mentor Interview**: all conversations, tab filter by recommendation, name search
- **Interviews**: project sent / project received, name search
- **Admin Menu**: Google Calendar events in a table, reminder mail to event participants through Gmail
- **Google Drive sync**: data files are downloaded from a Drive folder at startup when they have changed; local copies are used when offline
- Every page has the same visual style, with a separate accent color per section

## Requirements

- Python 3.11 or newer (tested with Python 3.14)
- Windows, macOS or Linux

Install the libraries:

```
pip install -r requirements.txt
```

## Running

```
python main.py          # windows built in Python code
python main.py --ui     # windows loaded from the Qt Designer .ui files
```

## Data

The application reads four Excel files from the `data/` folder (or downloads them from Google Drive at startup):

| File | Used by |
|---|---|
| `Users.xlsx` | Login (username, password, role) |
| `Applications.xlsx` | Applications page |
| `Interviews.xlsx` | Interviews page |
| `Mentor.xlsx` | Mentor Interview page and admin calendar mail |
| `VIT1.xlsx`, `VIT2.xlsx` | VIT filters (optional) |

Column names are matched by keywords, so small wording changes in the headers do not break the app.

## Google setup (optional, needed for Drive, Calendar and Gmail)

1. Create a project in the Google Cloud Console.
2. Enable **Google Drive API**, **Google Calendar API** and **Gmail API**.
3. Configure the OAuth consent screen and add your account as a test user.
4. Create an **OAuth client ID** of type *Desktop app* and download the JSON file.
5. Save it as `credentials/credentials.json`.
6. Run the app once and sign in in the browser. `credentials/token.json` is created automatically.

Without this setup the app still works with the local `data/` files, and the Google features show a message instead.

## Tests

```
python test_navigation.py
```

The test creates temporary sample files and replaces the Google calls with fake functions, so it does not touch real data or accounts.

## Project structure

```
main.py              main window and page navigation
data_store.py        Excel reading, search, filters, login check, Drive sync
google_services.py   Google Drive, Calendar and Gmail access
styles.py            shared stylesheet and page color themes
pages/               one module per window (code version)
ui/                  one Qt Designer .ui file per window
assets/              logo
test_navigation.py   navigation and data tests
check_drive.py       Drive connection check
```

## Authors

- Muhammed Said Sezgin
