import logging
import time
import os
import json
from typing import Optional

from google.oauth2 import service_account
from googleapiclient.discovery import build

logger = logging.getLogger(__name__)

try:
    from src import settings as _settings
except Exception:
    _settings = None

SPREADSHEET_ID = os.getenv("SPREADSHEET_ID") or (getattr(_settings, "SPREADSHEET_ID", None) if _settings else None)
DEFAULT_SHEET_NAME = "UTAMA-KAPITA"
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


def _get_service():
    """Create Sheets API service using credentials from environment variables."""
    v_raw = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
    v_creds = None

    if v_raw:
        try:
            v_info = json.loads(v_raw)
            v_creds = service_account.Credentials.from_service_account_info(v_info, scopes=SCOPES)
        except Exception as e:
            logger.error("Invalid GOOGLE_SERVICE_ACCOUNT_JSON: %s", e)
            raise
    else:
        v_creds = service_account.Credentials.from_service_account_file("credential.json", scopes=SCOPES)

    return build("sheets", "v4", credentials=v_creds)


def _find_row_for_pid(p_service, p_pid, p_sheet_name: str = DEFAULT_SHEET_NAME) -> Optional[int]:
    if not SPREADSHEET_ID:
        logger.error("[SHEET DEBUG] SPREADSHEET_ID belum terkonfigurasi di environment atau settings!")
        return None

    v_range_name = f"'{p_sheet_name}'!B:B"
    logger.info("[SHEET DEBUG] Mencari p_pid: '%s' (Type: %s) pada range: %s", p_pid, type(p_pid).__name__, v_range_name)

    try:
        v_result = p_service.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID, range=v_range_name
        ).execute()
    except Exception as e:
        logger.error("[SHEET DEBUG] Gagal mengambil data dari Google Sheet API: %s", str(e))
        raise e

    v_values = v_result.get("values", [])
    logger.info("[SHEET DEBUG] Total baris terbaca dari Kolom B: %d baris", len(v_values))

    if not v_values:
        logger.warning("[SHEET DEBUG] Kolom B kosong atau sheet '%s' tidak memiliki data.", p_sheet_name)
        return None

    # Normalisasi p_pid pencarian
    v_target_pid = str(p_pid).strip().split('.')[0]
    logger.info("[SHEET DEBUG] Target PID setelah normalisasi: '%s'", v_target_pid)

    for v_idx, v_row in enumerate(v_values, start=1):
        if not v_row:
            continue
        
        v_raw_val = v_row[0]
        v_cell_val = str(v_raw_val).strip().split('.')[0]
        
        # Cetak log 10 baris pertama atau saat ada match untuk pengecekan
        if v_idx <= 10 or v_cell_val == v_target_pid:
            logger.info("[SHEET DEBUG] Baris %d: Nilai Asli='%s' | Ter-normalisasi='%s' | Match=%s", 
                        v_idx, v_raw_val, v_cell_val, (v_cell_val == v_target_pid))
        
        if v_cell_val == v_target_pid:
            logger.info("[SHEET DEBUG] SUKSES! PID '%s' ditemukan di Baris %d", p_pid, v_idx)
            return v_idx

    logger.warning("[SHEET DEBUG] GAGAL! PID '%s' (target: '%s') TIDAK ditemukan di seluruh Kolom B.", p_pid, v_target_pid)
    return None


def update_kapita_for_pid(
    p_pid, 
    p_kapita_sesi1: str, 
    p_kapita_sesi2: str, 
    p_sheet_name: str = DEFAULT_SHEET_NAME, 
    p_max_retries: int = 3, 
    p_backoff: float = 1.0
) -> bool:
    """Update kolom J dan K untuk baris tempat kolom B == p_pid."""
    v_attempt = 0
    v_last_exc = None

    while v_attempt < p_max_retries:
        try:
            v_service = _get_service()
            v_row = _find_row_for_pid(v_service, p_pid, p_sheet_name)
            if v_row is None:
                logger.info("PID %s not found in sheet %s", p_pid, p_sheet_name)
                return False

            v_range_update = f"'{p_sheet_name}'!J{v_row}:K{v_row}"
            v_body = {"values": [[p_kapita_sesi1, p_kapita_sesi2]]}

            v_result = v_service.spreadsheets().values().update(
                spreadsheetId=SPREADSHEET_ID,
                range=v_range_update,
                valueInputOption="RAW",
                body=v_body,
            ).execute()

            v_updated = v_result.get("updatedCells", 0)
            logger.info("Updated pid %s row %s (updatedCells=%s)", p_pid, v_row, v_updated)
            return True

        except Exception as e:
            v_last_exc = e
            v_attempt += 1
            v_wait = p_backoff * (2 ** (v_attempt - 1))
            logger.warning("Attempt %s to update sheet failed: %s. Retrying in %.1fs...", v_attempt, str(e), v_wait)
            time.sleep(v_wait)

    logger.error("Failed to update kapita for pid %s after %s attempts: %s", p_pid, p_max_retries, str(v_last_exc))
    return False
