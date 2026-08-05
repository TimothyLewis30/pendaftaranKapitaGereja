import io
# pyrefly: ignore [missing-import]
import xlsxwriter
from datetime import datetime
import pytz
from src.dao.modul import dao_get_peserta_for_excel


def generate_excel_peserta(p_pilihan, p_sesi_1=None, p_sesi_2=None, p_gkode=None):
    """
    Menghasilkan file Excel berisi data peserta berdasarkan 4 pilihan:
    1. Cetak Semua data peserta order by id peserta
    2. Cetak Data Peserta order by Gereja
    3. Cetak Data Peserta Order By Kapita
    4. Cetak Data Peserta Pada sesi 1 dan sesi 2
    """
    p_pilihan = int(p_pilihan)
    if p_pilihan not in (1, 2, 3, 4):
        raise ValueError("Pilihan cetak excel tidak valid. Gunakan opsi 1, 2, 3, atau 4.")

    v_data = dao_get_peserta_for_excel(p_pilihan, p_sesi_1, p_sesi_2, p_gkode)

    v_out = io.BytesIO()
    workbook = xlsxwriter.Workbook(v_out)

    # Format Styles
    v_format_title = workbook.add_format({
        'bold': True,
        'font_size': 14,
        'font_color': '#1F4E78',
        'align': 'left',
        'valign': 'vcenter'
    })
    v_format_subtitle = workbook.add_format({
        'italic': True,
        'font_size': 10,
        'font_color': '#595959',
        'align': 'left',
        'valign': 'vcenter'
    })
    v_format_header = workbook.add_format({
        'bold': True,
        'font_color': '#FFFFFF',
        'bg_color': '#1F4E78',
        'align': 'center',
        'valign': 'vcenter',
        'border': 1
    })
    v_format_body = workbook.add_format({
        'border': 1,
        'valign': 'vcenter',
        'align': 'left'
    })
    v_format_body_center = workbook.add_format({
        'border': 1,
        'valign': 'vcenter',
        'align': 'center'
    })
    v_format_total = workbook.add_format({
        'bold': True,
        'bg_color': '#D9E1F2',
        'border': 1,
        'align': 'left',
        'valign': 'vcenter'
    })

    # Determine report titles and filename based on pilihan
    if p_pilihan == 1:
        v_title = "LAPORAN DATA PESERTA (ORDER BY ID)"
        v_filename = "Data_Peserta_Berdasarkan_ID"
    elif p_pilihan == 2:
        v_title = "LAPORAN DATA PESERTA (ORDER BY GEREJA)"
        v_filename = "Data_Peserta_Berdasarkan_Gereja"
    elif p_pilihan == 3:
        v_title = "LAPORAN DATA PESERTA (ORDER BY KAPITA)"
        v_filename = "Data_Peserta_Berdasarkan_Kapita"
    elif p_pilihan == 4:
        v_title = "LAPORAN DATA PESERTA (SESI 1 & SESI 2)"
        v_filename = "Data_Peserta_Sesi1_Sesi2.xlsx"

    worksheet = workbook.add_worksheet("Data Peserta")

    # Timezone conversion (+7 WIB)
    v_sysdate = datetime.utcnow()
    v_utc_plus_7 = pytz.timezone('Etc/GMT-7')
    v_sysdate = v_sysdate.replace(tzinfo=pytz.utc).astimezone(v_utc_plus_7)
    v_tanggal_cetak = datetime.strftime(v_sysdate, '%d-%m-%Y %H:%M:%S')

    # Row 0: Title
    worksheet.write(0, 0, v_title, v_format_title)
    # Row 1: Timestamp
    worksheet.write(1, 0, f"Tanggal Dicetak: {v_tanggal_cetak} WIB", v_format_subtitle)

    # Column Headers Required:
    # Nama, Email, NO TLP, Nama Gereja, Nama Kapita, Nama sesi 1, Nama Sesi 2, Register jam berapa
    v_headers = [
        "No / ID",
        "Nama",
        "Email",
        "NO TLP",
        "Nama Gereja",
        "Nama Kapita",
        "Nama Sesi 1",
        "Nama Sesi 2",
        "Register jam berapa"
    ]

    row = 3
    for col_idx, header_text in enumerate(v_headers):
        worksheet.write(row, col_idx, header_text, v_format_header)

    # Track maximum text length for dynamic column widths
    col_widths = [len(h) for h in v_headers]

    for idx, item in enumerate(v_data, start=1):
        row += 1
        
        # ID / No
        v_id_val = str(item.get('id', idx))
        
        # Nama
        v_nama = str(item.get('full_name') or '')
        
        # Email
        v_email = str(item.get('email') or '')
        
        # NO TLP
        v_phone = str(item.get('phone') or '')
        
        # Nama Gereja
        v_church_name = str(item.get('church_name') or '')
        
        # Sesi 1 & 2
        v_sesi_1_name = str(item.get('kapita_name_sesi_1') or '')
        v_sesi_2_name = str(item.get('kapita_name_sesi_2') or '')
        
        # Nama Kapita (Combined representation)
        if v_sesi_1_name and v_sesi_2_name:
            v_nama_kapita = f"Sesi 1: {v_sesi_1_name} | Sesi 2: {v_sesi_2_name}"
        elif v_sesi_1_name:
            v_nama_kapita = v_sesi_1_name
        elif v_sesi_2_name:
            v_nama_kapita = v_sesi_2_name
        else:
            v_nama_kapita = ""

        # Register jam berapa
        v_reg_at = item.get('registered_at')
        if isinstance(v_reg_at, datetime):
            v_reg_str = v_reg_at.strftime('%Y-%m-%d %H:%M:%S')
        elif v_reg_at:
            v_reg_str = str(v_reg_at)
        else:
            v_reg_str = ""

        row_values = [
            v_id_val,
            v_nama,
            v_email,
            v_phone,
            v_church_name,
            v_nama_kapita,
            v_sesi_1_name,
            v_sesi_2_name,
            v_reg_str
        ]

        worksheet.write(row, 0, v_id_val, v_format_body_center)
        worksheet.write(row, 1, v_nama, v_format_body)
        worksheet.write(row, 2, v_email, v_format_body)
        worksheet.write(row, 3, v_phone, v_format_body_center)
        worksheet.write(row, 4, v_church_name, v_format_body)
        worksheet.write(row, 5, v_nama_kapita, v_format_body)
        worksheet.write(row, 6, v_sesi_1_name, v_format_body)
        worksheet.write(row, 7, v_sesi_2_name, v_format_body)
        worksheet.write(row, 8, v_reg_str, v_format_body_center)

        # Update max column widths
        for c_idx, val in enumerate(row_values):
            col_widths[c_idx] = max(col_widths[c_idx], len(val))

    # Summary Row
    row += 1
    worksheet.merge_range(row, 0, row, 3, f"TOTAL PESERTA: {len(v_data)} Orang", v_format_total)
    for c_idx in range(4, len(v_headers)):
        worksheet.write(row, c_idx, "", v_format_total)

    # Set column widths with padding
    for c_idx, width in enumerate(col_widths):
        worksheet.set_column(c_idx, c_idx, max(width + 3, 12))

    workbook.close()
    return v_out.getvalue(), v_filename