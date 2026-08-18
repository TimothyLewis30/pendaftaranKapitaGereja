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
    print("\n[PRINT CHECK] === STEP 1: MENCOBA AUTENTIKASI GOOGLE API ===")
    v_raw = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
    v_creds = None

    if v_raw:
        print("[PRINT CHECK] Membaca credential dari Environment Variable 'GOOGLE_SERVICE_ACCOUNT_JSON'...")
        try:
            v_info = json.loads(v_raw)
            v_creds = service_account.Credentials.from_service_account_info(v_info, scopes=SCOPES)
            print("[PRINT CHECK] OK: Credential JSON berhasil di-parse.")
        except Exception as e:
            print(f"[PRINT CHECK] ERROR: Format GOOGLE_SERVICE_ACCOUNT_JSON tidak valid: {e}")
            raise
    else:
        print("[PRINT CHECK] Environment variable kosong, membaca dari file lokal 'credential.json'...")
        v_creds = service_account.Credentials.from_service_account_file("credential.json", scopes=SCOPES)
        print("[PRINT CHECK] OK: File credential.json berhasil dibaca.")

    v_service = build("sheets", "v4", credentials=v_creds)
    print("[PRINT CHECK] OK: Google Sheets API Service berhasil dibuat.")
    return v_service


def _find_row_for_pid(p_service, p_pid, p_sheet_name: str = DEFAULT_SHEET_NAME) -> Optional[int]:
    print("\n[PRINT CHECK] === STEP 2: PROSES PENCARIAN ROW DENGAN PID ===")
    print(f"[PRINT CHECK] Parameter Input -> p_pid: '{p_pid}' (tipe: {type(p_pid).__name__}), Sheet: '{p_sheet_name}'")
    print(f"[PRINT CHECK] SPREADSHEET_ID: '{SPREADSHEET_ID}'")

    if not SPREADSHEET_ID:
        print("[PRINT CHECK] ERROR FATAL: SPREADSHEET_ID kosong/tidak ditemukan di settings/env!")
        return None

    v_range_name = f"'{p_sheet_name}'!B:B"
    print(f"[PRINT CHECK] Mengambil data dari Google Sheet range: {v_range_name}...")

    try:
        v_result = p_service.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID, range=v_range_name
        ).execute()
        print("[PRINT CHECK] OK: Berhasil request data ke Google Sheets API.")
    except Exception as e:
        print(f"[PRINT CHECK] ERROR API: Gagal saat mengambil data dari Google Sheet -> {e}")
        raise e

    v_values = v_result.get("values", [])
    print(f"[PRINT CHECK] Total baris terbaca pada Kolom B: {len(v_values)} baris.")

    if not v_values:
        print(f"[PRINT CHECK] ERROR: Kolom B kosong atau Sheet '{p_sheet_name}' tidak ditemukan/tidak ada data.")
        return None

    v_target_pid = str(p_pid).strip().split('.')[0]
    print(f"[PRINT CHECK] Target PID setelah normalisasi: '{v_target_pid}'")
    print("[PRINT CHECK] Memulai pencocokan baris per baris...")

    for v_idx, v_row in enumerate(v_values, start=1):
        if not v_row:
            continue
        
        v_raw_val = v_row[0]
        v_cell_val = str(v_raw_val).strip().split('.')[0]
        
        # Cetak 5 baris pertama untuk memastikan isi sebenarnya dari kolom B
        if v_idx <= 5:
            print(f"   -> [Cek Baris {v_idx}] Nilai Sel Asli: '{v_raw_val}' | Hasil Clean: '{v_cell_val}' | Match: {v_cell_val == v_target_pid}")
        
        if v_cell_val == v_target_pid:
            print(f"[PRINT CHECK] MATCH SUKSES! Target PID '{v_target_pid}' cocok di BARIS KE-{v_idx} (Nilai Sel: '{v_raw_val}')")
            return v_idx

    print(f"[PRINT CHECK] GAGAL MATCH: Target PID '{v_target_pid}' TIDAK ditemukan di seluruh {len(v_values)} baris Kolom B.")
    return None


def update_kapita_for_pid(
    p_pid, 
    p_kapita_sesi1: str, 
    p_kapita_sesi2: str, 
    p_sheet_name: str = DEFAULT_SHEET_NAME, 
    p_max_retries: int = 3, 
    p_backoff: float = 1.0
) -> bool:
    print("\n=======================================================")
    print("[PRINT CHECK] MENJALANKAN FUNGSI update_kapita_for_pid")
    print(f"[PRINT CHECK] Payload -> PID: {p_pid}, Sesi 1: '{p_kapita_sesi1}', Sesi 2: '{p_kapita_sesi2}'")
    print("=======================================================")
    
    v_attempt = 0
    v_last_exc = None

    while v_attempt < p_max_retries:
        print(f"\n[PRINT CHECK] --- Percobaan Ke-{v_attempt + 1} dari {p_max_retries} ---")
        try:
            v_service = _get_service()
            v_row = _find_row_for_pid(v_service, p_pid, p_sheet_name)
            
            if v_row is None:
                print(f"[PRINT CHECK] HASIL: PID '{p_pid}' tidak ditemukan di sheet '{p_sheet_name}'. Update dibatalkan.")
                return False

            v_range_update = f"'{p_sheet_name}'!J{v_row}:K{v_row}"
            v_body = {"values": [[p_kapita_sesi1, p_kapita_sesi2]]}
            print(f"[PRINT CHECK] === STEP 3: MENGIRIM UPDATE KE GSHEET ===")
            print(f"[PRINT CHECK] Target Range: {v_range_update}")
            print(f"[PRINT CHECK] Body Data: {v_body}")

            v_result = v_service.spreadsheets().values().update(
                spreadsheetId=SPREADSHEET_ID,
                range=v_range_update,
                valueInputOption="RAW",
                body=v_body,
            ).execute()

            v_updated = v_result.get("updatedCells", 0)
            print(f"[PRINT CHECK] SUKSES BERHASIL! Updated Cells: {v_updated} pada baris {v_row}.")
            print("=======================================================\n")
            return True

        except Exception as e:
            v_last_exc = e
            v_attempt += 1
            v_wait = p_backoff * (2 ** (v_attempt - 1))
            print(f"[PRINT CHECK] EXCEPTION/ERROR PADA PERCOBAAN {v_attempt}: {e}")
            if v_attempt < p_max_retries:
                print(f"[PRINT CHECK] Menunggu {v_wait} detik sebelum retry...")
                time.sleep(v_wait)

    print(f"[PRINT CHECK] GAGAL TOTAL setelah {p_max_retries} kali percobaan. Error Terakhir: {v_last_exc}")
    print("=======================================================\n")
    return False
