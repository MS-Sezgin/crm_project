"""Drive connection check. Run: python check_drive.py

Shows each Drive data file and what the sync did with it.
Downloads only changed files, same as the app does at startup.
"""
import os

import data_store
import google_services

print("Drive folder:", google_services.DRIVE_FOLDER_ID)
print("Local data folder:", data_store.DATA_DIR)
print()

try:
    results = google_services.sync_drive_files(data_store.DATA_DIR, data_store.DRIVE_FILES)
except Exception as error:
    print("FAILED:", error)
    raise SystemExit(1)

for name in data_store.DRIVE_FILES:
    path = os.path.join(data_store.DATA_DIR, name)
    size = f"{os.path.getsize(path)} bytes" if os.path.exists(path) else "missing locally"
    print(f"{name:20} {results.get(name, '?'):12} {size}")

print()
print("Test finished. If the status is 'downloaded' or 'up to date', Drive works.")
