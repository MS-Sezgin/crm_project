"""Drive connection and freshness check. Run: python check_drive.py

1. Runs the same sync as the app and shows what happened to each file.
2. Shows, for each file, how many copies Drive has and when Drive says it was last changed,
   next to the local copy's modified time. Use this right after you edit a file in Drive.
"""
import os
from datetime import datetime

import data_store
import google_services

print("Local data folder:", data_store.DATA_DIR)
try:
    print("Drive folder:", google_services.drive_folder_id())
except google_services.GoogleSetupError as error:
    print("FAILED:", error)
    raise SystemExit(1)
print()

try:
    results = google_services.sync_drive_files(data_store.DATA_DIR, data_store.DRIVE_FILES)
except Exception as error:
    print("SYNC FAILED:", error)
    raise SystemExit(1)

for name in data_store.DRIVE_FILES:
    path = os.path.join(data_store.DATA_DIR, name)
    size = f"{os.path.getsize(path)} bytes" if os.path.exists(path) else "missing locally"
    print(f"{name:20} {results.get(name, '?'):12} {size}")

print()
print("Freshness check (times in your local time zone):")
from googleapiclient.discovery import build  # noqa: E402

service = build("drive", "v3", credentials=google_services._credentials(), cache_discovery=False)
for name in data_store.DRIVE_FILES:
    query = (f"'{google_services.drive_folder_id()}' in parents and "
             f"name = '{name}' and trashed = false")
    files = service.files().list(
        q=query, fields="files(id,name,modifiedTime)", orderBy="modifiedTime desc", pageSize=5,
    ).execute().get("files", [])
    path = os.path.join(data_store.DATA_DIR, name)
    local_time = datetime.fromtimestamp(os.path.getmtime(path)).astimezone() if os.path.exists(path) else None
    if files:
        drive_time = datetime.fromisoformat(files[0]["modifiedTime"].replace("Z", "+00:00")).astimezone()
        drive_text = drive_time.strftime("%d.%m.%Y %H:%M:%S")
    else:
        drive_text = "not in Drive folder"
    local_text = local_time.strftime("%d.%m.%Y %H:%M:%S") if local_time else "missing"
    print(f"{name:20} copies in Drive: {len(files)}  Drive changed: {drive_text}  local copy: {local_text}")

print()
print("If 'Drive changed' is newer than 'local copy', the app should download it on refresh.")
