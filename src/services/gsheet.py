import logging
import time
import os
import json
from typing import Optional

from google.oauth2 import service_account
from googleapiclient.discovery import build

logger = logging.getLogger(__name__)
# SPREADSHEET_ID must be the spreadsheet identifier (not credentials).
# Prefer environment variable, fallback to src.settings.SPREADSHEET_ID if available.
try:
    from src import settings as _settings
except Exception:
    _settings = None

SPREADSHEET_ID = os.getenv("SPREADSHEET_ID") or (getattr(_settings, "SPREADSHEET_ID", None) if _settings else None)
DEFAULT_SHEET_NAME = "UTAMA-KAPITA"
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


def _get_service():
    """Create Sheets API service using credentials from environment variables.

    Priority:
    1. GOOGLE_SERVICE_ACCOUNT_JSON (raw JSON)
    2. credential.json file (local dev fallback)
    """
    raw = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
    creds = None

    if raw:
        try:
            info = json.loads(raw)
            creds = service_account.Credentials.from_service_account_info(info, scopes=SCOPES)
        except Exception as e:
            logger.error("Invalid GOOGLE_SERVICE_ACCOUNT_JSON: %s", e)
            raise
    else:
        # Local fallback for development
        creds = service_account.Credentials.from_service_account_file("credential.json", scopes=SCOPES)

    return build("sheets", "v4", credentials=creds)


def _find_row_for_pid(service, pid: int, sheet_name: str = DEFAULT_SHEET_NAME) -> Optional[int]:
    if not SPREADSHEET_ID:
        logger.error("SPREADSHEET_ID is not configured in environment or settings.")
        return None

    range_name = f"'{sheet_name}'!B:B"
    result = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID, range=range_name
    ).execute()
    values = result.get("values", [])

    for idx, row in enumerate(values, start=1):
        cell = row[0] if len(row) > 0 else ""
        if str(cell).strip() == str(pid).strip():
            return idx
    return None


def update_kapita_for_pid(pid: int, kapita_sesi1: str, kapita_sesi2: str, sheet_name: str = DEFAULT_SHEET_NAME, max_retries: int = 3, backoff: float = 1.0) -> bool:
    """Update columns J and K for the row where column B == pid.

    Retries on transient errors with exponential backoff. Returns True on success.
    """
    attempt = 0
    last_exc = None
    while attempt < max_retries:
        try:
            service = _get_service()
            row = _find_row_for_pid(service, pid, sheet_name)
            if row is None:
                logger.info("PID %s not found in sheet %s", pid, sheet_name)
                return False

            range_update = f"'{sheet_name}'!J{row}:K{row}"
            body = {"values": [[kapita_sesi1, kapita_sesi2]]}

            result = service.spreadsheets().values().update(
                spreadsheetId=SPREADSHEET_ID,
                range=range_update,
                valueInputOption="RAW",
                body=body,
            ).execute()

            updated = result.get("updatedCells", 0)
            logger.info("Updated pid %s row %s (updatedCells=%s)", pid, row, updated)
            return True

        except Exception as e:
            last_exc = e
            attempt += 1
            wait = backoff * (2 ** (attempt - 1))
            logger.warning("Attempt %s to update sheet failed: %s. Retrying in %.1fs...", attempt, str(e), wait)
            time.sleep(wait)

    logger.error("Failed to update kapita for pid %s after %s attempts: %s", pid, max_retries, str(last_exc))
    return False
