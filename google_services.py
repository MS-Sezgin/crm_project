"""Google Calendar (read events) and Gmail (send mail) access.

One-time setup:
1. Google Cloud Console: create a project, enable "Google Calendar API" and "Gmail API".
2. OAuth consent screen: fill in the app name and add your Google account as a test user.
3. Credentials > Create credentials > OAuth client ID > Desktop app. Download the JSON file.
4. Save it as credentials/credentials.json inside the project folder.

The first call opens a browser for sign-in and creates credentials/token.json.
Google libraries are imported only when needed, so the rest of the app works without them.
"""
import base64
import hashlib
import json
import os
import time
from datetime import datetime, timedelta, timezone
from email.message import EmailMessage

from paths import app_dir

CREDENTIALS_DIR = os.environ.get("CRM_CREDENTIALS_DIR", os.path.join(app_dir(), "credentials"))
CLIENT_FILE = os.path.join(CREDENTIALS_DIR, "credentials.json")
TOKEN_FILE = os.path.join(CREDENTIALS_DIR, "token.json")
SCOPES = [
    "https://www.googleapis.com/auth/calendar.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/drive.readonly",
]


class GoogleSetupError(Exception):
    """Raised when Google libraries, credentials or sign-in are not ready."""


def _credentials():
    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
    except ImportError as error:
        raise GoogleSetupError("Google libraries are missing. Run: pip install -r requirements.txt") from error

    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if creds and not set(SCOPES).issubset(set(creds.scopes or [])):
        creds = None  # token was created before a scope was added: sign in again
    if creds and creds.valid:
        return creds
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        if not os.path.exists(CLIENT_FILE):
            raise GoogleSetupError(f"credentials.json was not found at {CLIENT_FILE}")
        flow = InstalledAppFlow.from_client_secrets_file(CLIENT_FILE, SCOPES)
        creds = flow.run_local_server(port=0)

    os.makedirs(CREDENTIALS_DIR, exist_ok=True)
    with open(TOKEN_FILE, "w", encoding="utf-8") as handle:
        handle.write(creds.to_json())
    return creds


def format_start(value):
    """Turn Google's ISO start time into dd.mm.yyyy HH:MM (date-only events stay as they are)."""
    if not value:
        return ""
    try:
        moment = datetime.fromisoformat(value)
    except ValueError:
        return value
    return moment.strftime("%d.%m.%Y %H:%M")


def calendar_id():
    """Calendar to read. Set it in credentials/calendar_id.txt (one line), so code updates do not reset it.

    Without that file the main calendar ("primary") is used.
    """
    path = os.path.join(CREDENTIALS_DIR, "calendar_id.txt")
    if os.path.exists(path):
        with open(path, encoding="utf-8") as handle:
            value = handle.read().strip()
        if value:
            return value
    return "primary"


def fetch_events(days_back=30, days_ahead=60, max_results=100):
    """Return a list of dicts: name, start, participants (list of e-mails), organizer."""
    from googleapiclient.discovery import build

    service = build("calendar", "v3", credentials=_credentials(), cache_discovery=False)
    now = datetime.now(timezone.utc)
    result = service.events().list(
        calendarId=calendar_id(),
        timeMin=(now - timedelta(days=days_back)).isoformat(),
        timeMax=(now + timedelta(days=days_ahead)).isoformat(),
        singleEvents=True,
        orderBy="startTime",
        maxResults=max_results,
    ).execute()

    events = []
    for item in result.get("items", []):
        start = item.get("start", {})
        attendees = [a["email"] for a in item.get("attendees", []) if a.get("email")]
        events.append({
            "name": item.get("summary", "(no title)"),
            "start": format_start(start.get("dateTime") or start.get("date", "")),
            "participants": attendees,
            "organizer": item.get("organizer", {}).get("email", ""),
        })
    return events


def send_email(recipients, subject, body):
    """Send a plain-text e-mail from the signed-in Gmail account."""
    from googleapiclient.discovery import build

    service = build("gmail", "v1", credentials=_credentials(), cache_discovery=False)
    message = EmailMessage()
    message["To"] = ", ".join(recipients)
    message["Subject"] = subject
    message.set_content(body)
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    service.users().messages().send(userId="me", body={"raw": raw}).execute()


def drive_folder_id():
    """ID of your Drive folder, read from credentials/drive_folder_id.txt (one line).

    Use the part after /folders/ in the folder link. Stored outside the code, so updates keep it.
    """
    path = os.path.join(CREDENTIALS_DIR, "drive_folder_id.txt")
    if not os.path.exists(path):
        raise GoogleSetupError(f"drive_folder_id.txt was not found at {path}")
    with open(path, encoding="utf-8") as handle:
        value = handle.read().strip()
    if not value:
        raise GoogleSetupError("drive_folder_id.txt is empty")
    return value


def _md5_of_file(path):
    digest = hashlib.md5()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


IDS_FILE = os.path.join(CREDENTIALS_DIR, "drive_file_ids.json")


def _load_ids():
    if not os.path.exists(IDS_FILE):
        return {}
    with open(IDS_FILE, encoding="utf-8") as handle:
        return json.load(handle)


def _save_ids(ids):
    os.makedirs(CREDENTIALS_DIR, exist_ok=True)
    with open(IDS_FILE, "w", encoding="utf-8") as handle:
        json.dump(ids, handle, indent=2)


def _find_file(service, folder_id, name, known_id):
    """Return the newest copy of a file in the Drive folder, or None.

    Drive's search (files.list) can lag a few minutes behind a fresh edit, so the
    file is also read directly by its id, which is always current. The newest of
    both answers is used.
    """
    from googleapiclient.errors import HttpError

    candidates = []
    if known_id:
        try:
            meta = service.files().get(
                fileId=known_id, fields="id,name,modifiedTime,md5Checksum,trashed,parents",
            ).execute()
            if not meta.get("trashed") and folder_id in meta.get("parents", []) and meta.get("name") == name:
                candidates.append(meta)
        except HttpError:
            pass  # id no longer valid, the search below finds the file again
    query = f"'{folder_id}' in parents and name = '{name}' and trashed = false"
    found = service.files().list(
        q=query, fields="files(id,name,modifiedTime,md5Checksum)", pageSize=10,
    ).execute()
    candidates.extend(found.get("files", []))
    if not candidates:
        return None
    return max(candidates, key=lambda meta: meta.get("modifiedTime", ""))


def sync_drive_files(target_dir, file_names):
    """Download files from the Drive data folder when their content differs from the local copy.

    Compares content checksums (md5), not timestamps. Returns
    {file_name: "downloaded" | "up to date" | "not found" | "retry later"}.
    "retry later": Drive served an older version than its metadata; the local copy is kept.
    """
    from googleapiclient.discovery import build

    folder_id = drive_folder_id()
    service = build("drive", "v3", credentials=_credentials(), cache_discovery=False)
    os.makedirs(target_dir, exist_ok=True)
    ids = _load_ids()
    results = {}
    try:
        for name in file_names:
            item = _find_file(service, folder_id, name, ids.get(name))
            if item is None:
                results[name] = "not found"
                ids.pop(name, None)
                continue
            ids[name] = item["id"]
            remote_md5 = item.get("md5Checksum")
            path = os.path.join(target_dir, name)

            if remote_md5 and os.path.exists(path) and _md5_of_file(path) == remote_md5:
                results[name] = "up to date"
                continue

            content = b""
            matched = False
            for attempt in range(3):
                content = service.files().get_media(fileId=item["id"]).execute()
                if not remote_md5 or hashlib.md5(content).hexdigest() == remote_md5:
                    matched = True
                    break
                time.sleep(2)
            if not matched:
                results[name] = "retry later"
                continue

            temp_path = path + ".part"
            with open(temp_path, "wb") as handle:
                handle.write(content)
            os.replace(temp_path, path)
            if item.get("modifiedTime"):
                remote_time = datetime.fromisoformat(item["modifiedTime"].replace("Z", "+00:00")).timestamp()
                os.utime(path, (remote_time, remote_time))
            results[name] = "downloaded"
    finally:
        _save_ids(ids)
    return results
