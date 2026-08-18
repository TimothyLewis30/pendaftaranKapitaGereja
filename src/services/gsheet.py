import logging
import time
import json
import os
from typing import Optional, Dict

from google.oauth2 import service_account
from googleapiclient.discovery import build

from src import settings

logger = logging.getLogger(__name__)

SPREADSHEET_ID = settings.SPREADSHEET_ID
DEFAULT_SHEET_NAME = "UTAMA-KAPITA"
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# Mapping kolom untuk Kapita-Sesi-1 & Kapita-Sesi-2 (ID 5 - 8)
# Format: ID_Kapita: (Kolom_Nama, Kolom_Gereja)
KAPITA_COLUMN_MAP: Dict[int, tuple] = {
    5: ("C", "D"),  # Kapita ID 5 -> Kolom C (Nama) & D (Gereja)
    6: ("H", "I"),  # Kapita ID 6 -> Kolom H (Nama) & I (Gereja)
    7: ("M", "N"),  # Kapita ID 7 -> Kolom M (Nama) & N (Gereja)
    8: ("R", "S"),  # Kapita ID 8 -> Kolom R (Nama) & S (Gereja)
}


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


def _find_row_for_pid(p_service, p_pid, p_sheet_name: str) -> Optional[int]:
    """Cari baris berdasarkan PID di Kolom B (digunakan khusus sheet UTAMA-KAPITA)."""
    v_range_name = f"'{p_sheet_name}'!B:B"
    print(f"[GSHEET] Mencari PID '{p_pid}' di sheet '{p_sheet_name}'...")

    try:
        v_result = p_service.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID, range=v_range_name
        ).execute()
    except Exception as e:
        print(f"[GSHEET] ❌ ERROR API pada sheet {p_sheet_name}: {e}")
        raise e

    v_values = v_result.get("values", [])
    if not v_values:
        print(f"[GSHEET] ⚠️ Sheet '{p_sheet_name}' atau Kolom B kosong.")
        return None

    v_target_pid = str(p_pid).strip().split('.')[0]

    for v_idx, v_row in enumerate(v_values, start=1):
        if not v_row:
            continue
        
        v_cell_val = str(v_row[0]).strip().split('.')[0]
        if v_cell_val == v_target_pid:
            print(f"[GSHEET] ✅ PID '{p_pid}' ditemukan di baris ke-{v_idx} pada sheet '{p_sheet_name}'")
            return v_idx

    print(f"[GSHEET] ⚠️ PID '{p_pid}' tidak ditemukan di sheet '{p_sheet_name}'")
    return None


def _find_next_empty_row_in_columns(p_service, p_sheet_name: str, p_col_name: str, p_start_row: int = 4) -> int:
    """Mencari baris kosong pertama pada kolom spesifik mulai dari p_start_row (default baris 4)."""
    v_range_name = f"'{p_sheet_name}'!{p_col_name}{p_start_row}:{p_col_name}"
    
    try:
        v_result = p_service.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID, range=v_range_name
        ).execute()
    except Exception as e:
        print(f"[GSHEET] ❌ ERROR saat mencari baris kosong di {p_sheet_name} kolom {p_col_name}: {e}")
        raise e

    v_values = v_result.get("values", [])
    
    if not v_values:
        return p_start_row

    for v_idx, v_row in enumerate(v_values):
        if not v_row or not str(v_row[0]).strip():
            return p_start_row + v_idx

    return p_start_row + len(v_values)


def _update_utama_kapita(
    p_service, 
    p_pid, 
    p_kapita_name_sesi1: str, 
    p_kapita_name_sesi2: str, 
    p_sheet_name: str = DEFAULT_SHEET_NAME
) -> bool:
    """Update nama pilihan Kapita Sesi 1 & 2 ke sheet UTAMA-KAPITA (Berdasarkan PID di Kolom B)."""
    v_row = _find_row_for_pid(p_service, p_pid, p_sheet_name)
    if v_row is None:
        return False

    v_range_update = f"'{p_sheet_name}'!J{v_row}:K{v_row}"
    v_body = {"values": [[p_kapita_name_sesi1, p_kapita_name_sesi2]]}

    print(f"[GSHEET] Updating '{p_sheet_name}' | Range: {v_range_update} | Data: [{p_kapita_name_sesi1}, {p_kapita_name_sesi2}]")

    v_result = p_service.spreadsheets().values().update(
        spreadsheetId=SPREADSHEET_ID,
        range=v_range_update,
        valueInputOption="RAW",
        body=v_body,
    ).execute()

    v_updated = v_result.get("updatedCells", 0)
    print(f"[GSHEET] ✅ Sukses update {p_sheet_name} (updatedCells={v_updated})")
    return True


def _append_to_single_session(
    p_service, 
    p_full_name: str, 
    p_church_name: str, 
    p_kapita_id: int, 
    p_sheet_name: str,
    p_start_row: int = 4
) -> bool:
    """Mengisi data Nama & Gereja ke baris baru yang kosong pada kolom Kapita target."""
    if not p_kapita_id or p_kapita_id not in KAPITA_COLUMN_MAP:
        print(f"[GSHEET] ⚠️ Kapita ID '{p_kapita_id}' tidak valid / tidak ada di mapping. Skip {p_sheet_name}.")
        return False

    v_col_name, v_col_church = KAPITA_COLUMN_MAP[p_kapita_id]

    v_target_row = _find_next_empty_row_in_columns(
        p_service=p_service, 
        p_sheet_name=p_sheet_name, 
        p_col_name=v_col_name, 
        p_start_row=p_start_row
    )

    v_range_update = f"'{p_sheet_name}'!{v_col_name}{v_target_row}:{v_col_church}{v_target_row}"
    v_body = {"values": [[p_full_name, p_church_name]]}

    print(f"[GSHEET] Inserting Row Baru '{p_sheet_name}' | Target Range: {v_range_update} | Data: [{p_full_name}, {p_church_name}]")

    v_result = p_service.spreadsheets().values().update(
        spreadsheetId=SPREADSHEET_ID,
        range=v_range_update,
        valueInputOption="RAW",
        body=v_body,
    ).execute()

    v_updated = v_result.get("updatedCells", 0)
    print(f"[GSHEET] ✅ Sukses mengisi baris ke-{v_target_row} pada {p_sheet_name} (updatedCells={v_updated})")
    return True


def update_kapita_for_pid(
    p_pid, 
    p_full_name: str,
    p_church_name: str,
    p_kapita_id_sesi1: int, 
    p_kapita_id_sesi2: int, 
    p_kapita_name_sesi1: str = "",
    p_kapita_name_sesi2: str = "",
    p_max_retries: int = 3, 
    p_backoff: float = 1.0,
    p_start_row: int = 4
) -> bool:
    """
    1. Update UTAMA-KAPITA -> Berdasarkan PID (Overwrites Kolom J & K)
    2. Kapita-Sesi-1 -> Mencari baris kosong mulai dari baris 4 di kolom Kapita terkait
    3. Kapita-Sesi-2 -> Mencari baris kosong mulai dari baris 4 di kolom Kapita terkait
    """
    print("\n=======================================================")
    print("[GSHEET] MENJALANKAN PROCESS SINKRONISASI GSHEET")
    print(f"[GSHEET] PID: {p_pid} | Nama: {p_full_name} | Gereja: {p_church_name}")
    print(f"[GSHEET] Sesi 1: ID {p_kapita_id_sesi1} ({p_kapita_name_sesi1})")
    print(f"[GSHEET] Sesi 2: ID {p_kapita_id_sesi2} ({p_kapita_name_sesi2})")
    print("=======================================================")

    v_attempt = 0
    v_last_exc = None

    while v_attempt < p_max_retries:
        try:
            v_service = _get_service()

            # 1. Update ke Sheet UTAMA-KAPITA (Berdasarkan PID)
            if p_kapita_name_sesi1 or p_kapita_name_sesi2:
                _update_utama_kapita(
                    p_service=v_service,
                    p_pid=p_pid,
                    p_kapita_name_sesi1=p_kapita_name_sesi1,
                    p_kapita_name_sesi2=p_kapita_name_sesi2
                )

            # 2. Append ke Sheet Kapita-Sesi-1 (Mencari baris kosong mulai dari baris 4)
            _append_to_single_session(
                p_service=v_service,
                p_full_name=p_full_name,
                p_church_name=p_church_name,
                p_kapita_id=p_kapita_id_sesi1,
                p_sheet_name="Kapita-Sesi-1",
                p_start_row=p_start_row
            )

            # 3. Append ke Sheet Kapita-Sesi-2 (Mencari baris kosong mulai dari baris 4)
            _append_to_single_session(
                p_service=v_service,
                p_full_name=p_full_name,
                p_church_name=p_church_name,
                p_kapita_id=p_kapita_id_sesi2,
                p_sheet_name="Kapita-Sesi-2",
                p_start_row=p_start_row
            )

            print("=======================================================\n")
            return True

        except Exception as e:
            v_last_exc = e
            v_attempt += 1
            v_wait = p_backoff * (2 ** (v_attempt - 1))
            print(f"[GSHEET] ❌ Attempt {v_attempt} gagal: {e}. Retry dalam {v_wait}s...")
            time.sleep(v_wait)

    logger.error("Failed to update kapita for pid %s: %s", p_pid, str(v_last_exc))
    print("=======================================================\n")
    return False
