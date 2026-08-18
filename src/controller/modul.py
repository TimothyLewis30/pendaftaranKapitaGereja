"""
controller/modul.py
Business logic untuk semua modul (gabungan).
"""
from src.utils import responseJson
from src.utils.exceptions import ServiceException
from src.validasi.validate import validasi, require_role
from src.dao.modul import (
    dao_ping,
    dao_create_admin, dao_get_all_admins, dao_get_admin_by_id,
    dao_get_admin_by_email, dao_get_admin_with_password_by_id,
    dao_update_admin, dao_delete_admin,
    dao_get_all_churches, dao_get_church_by_gkode, dao_create_church,
    dao_update_church, dao_delete_church,
    dao_set_church_kapita_quota, dao_get_church_kapita_quotas,
    dao_get_quota_by_church_and_kapita, dao_delete_church_kapita_quota,
    dao_count_all_registrations_by_church, dao_count_all_users_by_church,
    dao_create_kapita, dao_get_all_kapita, dao_get_kapita_by_id,
    dao_update_kapita, dao_delete_kapita,
    dao_create_registration, dao_get_registration_by_id,
    dao_count_registrations_by_church_and_kapita,
    dao_update_registration, dao_delete_registration,
    dao_create_user, dao_get_all_users, dao_get_user_by_id,
    dao_update_user, dao_delete_user, dao_count_users_by_church_and_kapita,
    dao_get_participants_by_church, dao_get_participant_by_id,
)
from src.services.gsheet import update_kapita_for_pid
from werkzeug.security import generate_password_hash, check_password_hash


def _compute_effective_left(p_church_gkode, p_kapita_id, p_sesi):
    v_quota = dao_get_quota_by_church_and_kapita(p_church_gkode, p_kapita_id)
    if not v_quota:
        return None, None, None
    v_effective_kuota = v_quota[f"kuota_sesi_{p_sesi}"]
    v_effective_left = v_quota[f"quota_left_sesi_{p_sesi}"]
    return v_effective_kuota, v_effective_left, v_quota


# ═══════════════════════════════════════════════════════════════════════════════
# PING
# ═══════════════════════════════════════════════════════════════════════════════

def ctrl_ping():
    return dao_ping()


# ═══════════════════════════════════════════════════════════════════════════════
# ADMIN
# ═══════════════════════════════════════════════════════════════════════════════

@validasi
def ctrl_admin_login(p_email, p_password):
    v_admin = dao_get_admin_by_email(p_email)
    if not v_admin:
        raise ServiceException(status_code=401, detail="Email atau password salah.")
    if not check_password_hash(v_admin["apassword"], p_password):
        raise ServiceException(status_code=401, detail="Email atau password salah PASSWORD GTW KINK.")
    return {"aid": v_admin["aid"], "username": v_admin["ausername"], "email": v_admin["aemail"], "role": v_admin["arole"]}


@validasi
@require_role("SuperAdmin")
def ctrl_create_admin(p_username, p_email, p_password, p_role, **kwargs):
    v_existing = dao_get_admin_by_email(p_email)
    if v_existing:
        raise ServiceException(status_code=409, detail=f"Email '{p_email}' sudah digunakan.")
    if p_role is not None and p_role not in ("Admin", "SuperAdmin", "NULL"):
        raise ServiceException(status_code=400, detail=f"Role '{p_role}' tidak valid.")
    v_hash = generate_password_hash(p_password)
    v_new_id = dao_create_admin(p_username, p_email, v_hash, p_role)
    v_admin = dao_get_admin_by_id(v_new_id)
    return {"aid": v_admin["aid"], "username": v_admin["ausername"], "email": v_admin["aemail"], "role": v_admin["arole"]}


@validasi
@require_role("SuperAdmin")
def ctrl_get_all_admins(**kwargs):
    return [{"aid": v["aid"], "username": v["ausername"], "email": v["aemail"], "role": v["arole"]} for v in dao_get_all_admins()]


@validasi
@require_role("SuperAdmin")
def ctrl_get_admin_by_id(p_aid, **kwargs):
    v_admin = dao_get_admin_by_id(p_aid)
    if not v_admin:
        raise ServiceException(status_code=404, detail=f"Admin dengan ID {p_aid} tidak ditemukan.")
    return {"aid": v_admin["aid"], "username": v_admin["ausername"], "email": v_admin["aemail"], "role": v_admin["arole"]}


@validasi
@require_role("SuperAdmin")
def ctrl_update_admin(p_aid, p_username, p_email, p_password, p_role, **kwargs):
    v_admin = dao_get_admin_with_password_by_id(p_aid)
    if not v_admin:
        raise ServiceException(status_code=404, detail=f"Admin dengan ID {p_aid} tidak ditemukan.")
    if p_email is not None and p_email != v_admin["aemail"]:
        v_existing = dao_get_admin_by_email(p_email)
        if v_existing:
            raise ServiceException(status_code=409, detail=f"Email '{p_email}' sudah digunakan.")
    if p_role is not None and p_role not in ("Admin", "SuperAdmin", "NULL"):
        raise ServiceException(status_code=400, detail=f"Role '{p_role}' tidak valid.")
    v_hash = generate_password_hash(p_password) if p_password else None
    dao_update_admin(p_aid, p_username, p_email, v_hash, p_role)
    v_updated = dao_get_admin_by_id(p_aid)
    return {"aid": v_updated["aid"], "username": v_updated["ausername"], "email": v_updated["aemail"], "role": v_updated["arole"]}


@validasi
@require_role("SuperAdmin")
def ctrl_delete_admin(p_aid, **kwargs):
    v_admin = dao_get_admin_by_id(p_aid)
    if not v_admin:
        raise ServiceException(status_code=404, detail=f"Admin dengan ID {p_aid} tidak ditemukan.")
    return dao_delete_admin(p_aid)


# ═══════════════════════════════════════════════════════════════════════════════
# GEREJA
# ═══════════════════════════════════════════════════════════════════════════════

def _build_church_response(p_church, p_kapita_quotas):
    v_result_kapita = []
    v_any_kapita_available = False

    for k in p_kapita_quotas or []:
        v_kuota_sesi_1 = k.get("kuota_sesi_1", 0)
        v_kuota_sesi_2 = k.get("kuota_sesi_2", 0)
        v_left_sesi_1 = k.get("quota_left_sesi_1", 0)
        v_left_sesi_2 = k.get("quota_left_sesi_2", 0)
        v_flag_sesi_1 = "T" if v_left_sesi_1 > 0 else "F"
        v_flag_sesi_2 = "T" if v_left_sesi_2 > 0 else "F"
        if v_left_sesi_1 > 0 or v_left_sesi_2 > 0:
            v_any_kapita_available = True

        v_result_kapita.append({
            "gkid": k.get("gkid"),
            "gkode": k.get("gkode"),
            "idkapita": k.get("idkapita"),
            "kapita_name": k.get("kapita_name"),
            "kuota_sesi_1": v_kuota_sesi_1,
            "kuota_sesi_2": v_kuota_sesi_2,
            "registered_sesi_1": k.get("registered_sesi_1", 0),
            "registered_sesi_2": k.get("registered_sesi_2", 0),
            "quota_left_sesi_1": v_left_sesi_1,
            "quota_left_sesi_2": v_left_sesi_2,
            "effective_kuota_sesi_1": v_kuota_sesi_1,
            "effective_kuota_sesi_2": v_kuota_sesi_2,
            "effective_left_sesi_1": v_left_sesi_1,
            "effective_left_sesi_2": v_left_sesi_2,
            "flag_sesi_1": v_flag_sesi_1,
            "flag_sesi_2": v_flag_sesi_2,
            "effective_left": v_left_sesi_1 + v_left_sesi_2,
            "flag_kapita": "T" if (v_left_sesi_1 > 0 or v_left_sesi_2 > 0) else "F",
        })

    v_total_kuota_sesi_1 = sum(k["kuota_sesi_1"] for k in v_result_kapita)
    v_total_kuota_sesi_2 = sum(k["kuota_sesi_2"] for k in v_result_kapita)
    v_total_reg_sesi_1 = sum(k["registered_sesi_1"] for k in v_result_kapita)
    v_total_reg_sesi_2 = sum(k["registered_sesi_2"] for k in v_result_kapita)
    v_total_left_sesi_1 = v_total_kuota_sesi_1 - v_total_reg_sesi_1
    v_total_left_sesi_2 = v_total_kuota_sesi_2 - v_total_reg_sesi_2
    v_flag_gereja = "T" if (v_total_left_sesi_1 > 0 or v_total_left_sesi_2 > 0) else "F"

    return {
        "id": p_church["gkode"],
        "name": p_church["name"],
        "kuota_sesi_1": v_total_kuota_sesi_1,
        "kuota_sesi_2": v_total_kuota_sesi_2,
        "registered_sesi_1": v_total_reg_sesi_1,
        "registered_sesi_2": v_total_reg_sesi_2,
        "quota_left_sesi_1": v_total_left_sesi_1,
        "quota_left_sesi_2": v_total_left_sesi_2,
        "flag_sesi_1": "T" if v_total_left_sesi_1 > 0 else "F",
        "flag_sesi_2": "T" if v_total_left_sesi_2 > 0 else "F",
        "total_quota": v_total_kuota_sesi_1 + v_total_kuota_sesi_2,
        "total_registered": v_total_reg_sesi_1 + v_total_reg_sesi_2,
        "quota_left": v_total_left_sesi_1 + v_total_left_sesi_2,
        "flag_gereja": v_flag_gereja,
        "kapita": v_result_kapita,
    }


@validasi
def ctrl_get_all_churches():
    v_churches = dao_get_all_churches()
    v_result = []
    for v_church in v_churches:
        v_kapita_quotas = dao_get_church_kapita_quotas(v_church["gkode"])
        v_result.append(_build_church_response(v_church, v_kapita_quotas))
    return v_result


@validasi
def ctrl_get_church_detail(p_church_gkode):
    v_church = dao_get_church_by_gkode(p_church_gkode)
    if not v_church:
        raise ServiceException(status_code=404, detail=f"Gereja dengan kode {p_church_gkode} tidak ditemukan.")
    v_kapita_quotas = dao_get_church_kapita_quotas(p_church_gkode)
    return _build_church_response(v_church, v_kapita_quotas)


@validasi
@require_role("Admin", "SuperAdmin")
def ctrl_create_church(p_name, **kwargs):
    v_new_gkode = dao_create_church(p_name)
    v_all_kapita = dao_get_all_kapita()
    for v_k in v_all_kapita:
        dao_set_church_kapita_quota(v_new_gkode, v_k["idkapita"], 0, 0)
    v_church = dao_get_church_by_gkode(v_new_gkode)
    v_kapita_quotas = dao_get_church_kapita_quotas(v_new_gkode)
    return _build_church_response(v_church, v_kapita_quotas)


@validasi
@require_role("Admin", "SuperAdmin")
def ctrl_update_church(p_church_gkode, p_name, **kwargs):
    v_church = dao_get_church_by_gkode(p_church_gkode)
    if not v_church:
        raise ServiceException(status_code=404, detail=f"Gereja dengan kode {p_church_gkode} tidak ditemukan.")
    dao_update_church(p_church_gkode, p_name)
    v_updated = dao_get_church_by_gkode(p_church_gkode)
    v_kapita_quotas = dao_get_church_kapita_quotas(p_church_gkode)
    return _build_church_response(v_updated, v_kapita_quotas)


@validasi
@require_role("Admin", "SuperAdmin")
def ctrl_delete_church(p_church_gkode, **kwargs):
    v_church = dao_get_church_by_gkode(p_church_gkode)
    if not v_church:
        raise ServiceException(status_code=404, detail=f"Gereja dengan kode {p_church_gkode} tidak ditemukan.")
    return dao_delete_church(p_church_gkode)


# ═══════════════════════════════════════════════════════════════════════════════
# GEREJA_KAPITA QUOTA
# ═══════════════════════════════════════════════════════════════════════════════

@validasi
@require_role("Admin", "SuperAdmin")
def ctrl_set_church_kapita_quota(p_church_gkode, p_kapita_id, p_kuota_sesi_1, p_kuota_sesi_2, **kwargs):
    v_church = dao_get_church_by_gkode(p_church_gkode)
    if not v_church:
        raise ServiceException(status_code=404, detail=f"Gereja dengan kode {p_church_gkode} tidak ditemukan.")
    v_kapita = dao_get_kapita_by_id(p_kapita_id)
    if not v_kapita:
        raise ServiceException(status_code=404, detail=f"Kapita dengan ID {p_kapita_id} tidak ditemukan.")
    dao_set_church_kapita_quota(p_church_gkode, p_kapita_id, p_kuota_sesi_1, p_kuota_sesi_2)
    v_quota = dao_get_quota_by_church_and_kapita(p_church_gkode, p_kapita_id)
    return {
        "gkid": v_quota["gkid"],
        "gkode": v_quota["gkode"],
        "idkapita": v_quota["idkapita"],
        "kapita_name": v_kapita["namakapita"],
        "kuota_sesi_1": v_quota["kuota_sesi_1"],
        "kuota_sesi_2": v_quota["kuota_sesi_2"],
        "registered_sesi_1": v_quota["registered_sesi_1"],
        "registered_sesi_2": v_quota["registered_sesi_2"],
        "quota_left_sesi_1": v_quota["quota_left_sesi_1"],
        "quota_left_sesi_2": v_quota["quota_left_sesi_2"],
        "effective_kuota_sesi_1": v_quota["kuota_sesi_1"],
        "effective_kuota_sesi_2": v_quota["kuota_sesi_2"],
        "effective_left_sesi_1": v_quota["quota_left_sesi_1"],
        "effective_left_sesi_2": v_quota["quota_left_sesi_2"],
        "flag_sesi_1": "T" if v_quota["quota_left_sesi_1"] > 0 else "F",
        "flag_sesi_2": "T" if v_quota["quota_left_sesi_2"] > 0 else "F",
    }


@validasi
def ctrl_get_church_kapita_quotas(p_church_gkode):
    v_church = dao_get_church_by_gkode(p_church_gkode)
    if not v_church:
        raise ServiceException(status_code=404, detail=f"Gereja dengan kode {p_church_gkode} tidak ditemukan.")
    v_quotas = dao_get_church_kapita_quotas(p_church_gkode)
    v_result = []
    for k in v_quotas:
        v_result.append({
            **k,
            "effective_kuota_sesi_1": k["kuota_sesi_1"],
            "effective_kuota_sesi_2": k["kuota_sesi_2"],
            "effective_left_sesi_1": k["quota_left_sesi_1"],
            "effective_left_sesi_2": k["quota_left_sesi_2"],
            "flag_sesi_1": "T" if k["quota_left_sesi_1"] > 0 else "F",
            "flag_sesi_2": "T" if k["quota_left_sesi_2"] > 0 else "F",
            "effective_left": k["quota_left_sesi_1"] + k["quota_left_sesi_2"],
            "flag_kapita": "T" if (k["quota_left_sesi_1"] > 0 or k["quota_left_sesi_2"] > 0) else "F",
        })
    return v_result


@validasi
def ctrl_get_church_kapita_quota_detail(p_church_gkode, p_kapita_id):
    v_quota = dao_get_quota_by_church_and_kapita(p_church_gkode, p_kapita_id)
    if not v_quota:
        raise ServiceException(status_code=404, detail=f"Kuota untuk gereja {p_church_gkode} kapita {p_kapita_id} tidak ditemukan.")
    v_kapita = dao_get_kapita_by_id(p_kapita_id)
    return {
        "gkid": v_quota["gkid"],
        "gkode": v_quota["gkode"],
        "idkapita": v_quota["idkapita"],
        "kapita_name": v_kapita["namakapita"] if v_kapita else "",
        "kuota_sesi_1": v_quota["kuota_sesi_1"],
        "kuota_sesi_2": v_quota["kuota_sesi_2"],
        "registered_sesi_1": v_quota["registered_sesi_1"],
        "registered_sesi_2": v_quota["registered_sesi_2"],
        "quota_left_sesi_1": v_quota["quota_left_sesi_1"],
        "quota_left_sesi_2": v_quota["quota_left_sesi_2"],
        "effective_kuota_sesi_1": v_quota["kuota_sesi_1"],
        "effective_kuota_sesi_2": v_quota["kuota_sesi_2"],
        "effective_left_sesi_1": v_quota["quota_left_sesi_1"],
        "effective_left_sesi_2": v_quota["quota_left_sesi_2"],
        "flag_sesi_1": "T" if v_quota["quota_left_sesi_1"] > 0 else "F",
        "flag_sesi_2": "T" if v_quota["quota_left_sesi_2"] > 0 else "F",
    }


@validasi
@require_role("Admin", "SuperAdmin")
def ctrl_delete_church_kapita_quota(p_church_gkode, p_kapita_id, **kwargs):
    v_quota = dao_get_quota_by_church_and_kapita(p_church_gkode, p_kapita_id)
    if not v_quota:
        raise ServiceException(status_code=404, detail=f"Kuota untuk gereja {p_church_gkode} kapita {p_kapita_id} tidak ditemukan.")
    return dao_delete_church_kapita_quota(p_church_gkode, p_kapita_id)


# ═══════════════════════════════════════════════════════════════════════════════
# KAPITA
# ═══════════════════════════════════════════════════════════════════════════════

@validasi
@require_role("Admin", "SuperAdmin")
def ctrl_create_kapita(p_namakapita, **kwargs):
    v_new_id = dao_create_kapita(p_namakapita)
    v_data = dao_get_kapita_by_id(v_new_id)
    return {"idkapita": v_data["idkapita"], "namakapita": v_data["namakapita"]}


@validasi
def ctrl_get_all_kapita():
    return [{"idkapita": v["idkapita"], "namakapita": v["namakapita"]} for v in dao_get_all_kapita()]


@validasi
def ctrl_get_kapita_by_id(p_idkapita):
    v_data = dao_get_kapita_by_id(p_idkapita)
    if not v_data:
        raise ServiceException(status_code=404, detail=f"Kapita dengan ID {p_idkapita} tidak ditemukan.")
    return {"idkapita": v_data["idkapita"], "namakapita": v_data["namakapita"]}


@validasi
@require_role("Admin", "SuperAdmin")
def ctrl_update_kapita(p_idkapita, p_namakapita, **kwargs):
    v_data = dao_get_kapita_by_id(p_idkapita)
    if not v_data:
        raise ServiceException(status_code=404, detail=f"Kapita dengan ID {p_idkapita} tidak ditemukan.")
    dao_update_kapita(p_idkapita, p_namakapita)
    v_updated = dao_get_kapita_by_id(p_idkapita)
    return {"idkapita": v_updated["idkapita"], "namakapita": v_updated["namakapita"]}


@validasi
@require_role("Admin", "SuperAdmin")
def ctrl_delete_kapita(p_idkapita, **kwargs):
    v_data = dao_get_kapita_by_id(p_idkapita)
    if not v_data:
        raise ServiceException(status_code=404, detail=f"Kapita dengan ID {p_idkapita} tidak ditemukan.")
    return dao_delete_kapita(p_idkapita)


# ═══════════════════════════════════════════════════════════════════════════════
# REGISTRATIONS
# ═══════════════════════════════════════════════════════════════════════════════

@validasi
def ctrl_create_registration(p_payload):
    v_participant = dao_get_participant_by_id(p_payload.uparticipant)
    if not v_participant:
        raise ServiceException(status_code=404, detail=f"Peserta dengan ID {p_payload.uparticipant} tidak ditemukan.")
    if v_participant["pflag"] == "F":
        raise ServiceException(status_code=400, detail=f"Peserta '{v_participant['pnama']}' sudah terdaftar.")

    v_church = dao_get_church_by_gkode(v_participant["pgereja"])
    if not v_church:
        raise ServiceException(status_code=404, detail=f"Gereja dengan kode {v_participant['pgereja']} tidak ditemukan.")

    v_kapita_1 = dao_get_kapita_by_id(p_payload.kapita_id_sesi_1)
    if not v_kapita_1:
        raise ServiceException(status_code=404, detail=f"Kapita Sesi 1 dengan ID {p_payload.kapita_id_sesi_1} tidak ditemukan.")

    v_kapita_2 = dao_get_kapita_by_id(p_payload.kapita_id_sesi_2)
    if not v_kapita_2:
        raise ServiceException(status_code=404, detail=f"Kapita Sesi 2 dengan ID {p_payload.kapita_id_sesi_2} tidak ditemukan.")

    v_eff_kuota_1, v_eff_left_1, v_quota_1 = _compute_effective_left(v_participant["pgereja"], p_payload.kapita_id_sesi_1, 1)
    if v_quota_1 is None:
        raise ServiceException(status_code=400, detail=f"Kuota untuk gereja '{v_church['name']}' kapita '{v_kapita_1['namakapita']}' belum diatur.")

    v_eff_kuota_2, v_eff_left_2, v_quota_2 = _compute_effective_left(v_participant["pgereja"], p_payload.kapita_id_sesi_2, 2)
    if v_quota_2 is None:
        raise ServiceException(status_code=400, detail=f"Kuota untuk gereja '{v_church['name']}' kapita '{v_kapita_2['namakapita']}' belum diatur.")

    if p_payload.kapita_id_sesi_1 == p_payload.kapita_id_sesi_2:
        if v_eff_left_1 < 1 or v_eff_left_2 < 1:
            raise ServiceException(
                status_code=400,
                detail=f"Kapita '{v_kapita_1['namakapita']}' tidak cukup untuk mendaftar 2 sesi sekaligus (sisa sesi 1: {v_eff_left_1}, sisa sesi 2: {v_eff_left_2})."
            )
    else:
        v_errors = []
        if v_eff_left_1 <= 0:
            v_errors.append(f"Sesi 1 - Kapita '{v_kapita_1['namakapita']}' sudah penuh (kuota: {v_eff_kuota_1}, terdaftar: {v_quota_1['registered_sesi_1']})")
        if v_eff_left_2 <= 0:
            v_errors.append(f"Sesi 2 - Kapita '{v_kapita_2['namakapita']}' sudah penuh (kuota: {v_eff_kuota_2}, terdaftar: {v_quota_2['registered_sesi_2']})")
        if v_errors:
            raise ServiceException(status_code=400, detail="; ".join(v_errors))

    v_new_id = dao_create_registration(
        p_unama=v_participant["pnama"], p_ugereja=v_participant["pgereja"],
        p_kapita_id_sesi_1=p_payload.kapita_id_sesi_1, p_kapita_id_sesi_2=p_payload.kapita_id_sesi_2,
        p_uparticipant=p_payload.uparticipant,
    )
    v_saved = dao_get_registration_by_id(v_new_id)
    print("HASIL DARI V_SAVED",v_saved)
    if not v_saved:
        raise ServiceException(status_code=500, detail="Gagal mengambil data pendaftaran setelah disimpan.")

    # ----------------------------------------------------------------------------------------------------------------------------------------
    # ----------------------------------------------------------------------------------------------------------------------------------------
    # ----------------------------------------------------------------------------------------------------------------------------------------
    # ----------------------------------------------------------------------------------------------------------------------------------------
    # ----------------------------------------------------------------------------------------------------------------------------------------
    # Jika v_saved mengembalikan dictionary objek langsung:
    if  "uid" in v_saved:
        v_new_id = v_saved["uid"]
        v_update_gsheet  = update_kapita_for_pid(v_saved["uparticipant"], v_saved.get("kapita_name_sesi_1", ""), v_saved.get("kapita_name_sesi_2", ""))
        print("HASIL DARI UPDATE GSHEET 1",v_update_gsheet)
    
    # Jika v_saved dibungkus dalam key 'results':
    elif v_saved and "results" in v_saved and len(v_saved["results"]) > 0:
        v_new_id = v_saved["results"][0]["uid"]
        v_update_gsheet  = update_kapita_for_pid(v_saved["uparticipant"], v_saved.get("kapita_name_sesi_1", ""), v_saved.get("kapita_name_sesi_2", ""))
        print("HASIL DARI UPDATE GSHEET 2",v_update_gsheet)
    
    # Jika struktur tidak sesuai / terjadi error:
    else:
        raise ValueError(f"Gagal mengambil UID. Respons data: {v_saved}")
        
    # v_saved = dao_get_user_by_id(v_new_id)
    # if not v_saved:
    #     raise ServiceException(status_code=500, detail="Gagal mengambil data user setelah disimpan.")
    # update Google Sheet if service available

    
    return {
        "id": v_saved["uid"],
        "full_name": v_saved["full_name"],
        "church_gkode": v_saved["church_gkode"], "church_name": v_saved["church_name"],
        "kapita_id_sesi_1": v_saved["kapita_id_sesi_1"], "kapita_name_sesi_1": v_saved["kapita_name_sesi_1"],
        "kapita_id_sesi_2": v_saved["kapita_id_sesi_2"], "kapita_name_sesi_2": v_saved["kapita_name_sesi_2"],
        "uparticipant": v_saved["uparticipant"],
        "registered_at": str(v_saved["registered_at"]),
    }


@validasi
def ctrl_get_registration_by_id(p_reg_id):
    v_reg = dao_get_registration_by_id(p_reg_id)
    if not v_reg:
        raise ServiceException(status_code=404, detail=f"Pendaftaran dengan ID {p_reg_id} tidak ditemukan.")
    return {
        "id": v_reg["uid"],
        "full_name": v_reg["full_name"],
        "church_gkode": v_reg["church_gkode"], "church_name": v_reg["church_name"],
        "kapita_id_sesi_1": v_reg["kapita_id_sesi_1"], "kapita_name_sesi_1": v_reg["kapita_name_sesi_1"],
        "kapita_id_sesi_2": v_reg["kapita_id_sesi_2"], "kapita_name_sesi_2": v_reg["kapita_name_sesi_2"],
        "uparticipant": v_reg["uparticipant"],
        "registered_at": str(v_reg["registered_at"]),
    }


@validasi
def ctrl_update_registration(p_reg_id, p_payload):
    v_reg = dao_get_registration_by_id(p_reg_id)
    if not v_reg:
        raise ServiceException(status_code=404, detail=f"Pendaftaran dengan ID {p_reg_id} tidak ditemukan.")

    v_participant = dao_get_participant_by_id(p_payload.uparticipant)
    if not v_participant:
        raise ServiceException(status_code=404, detail=f"Peserta dengan ID {p_payload.uparticipant} tidak ditemukan.")
    if v_participant["pflag"] == "F" and v_reg["uparticipant"] != p_payload.uparticipant:
        raise ServiceException(status_code=400, detail=f"Peserta '{v_participant['pnama']}' sudah terdaftar.")

    v_church = dao_get_church_by_gkode(v_participant["pgereja"])
    if not v_church:
        raise ServiceException(status_code=404, detail=f"Gereja dengan kode {v_participant['pgereja']} tidak ditemukan.")

    v_kapita_1 = dao_get_kapita_by_id(p_payload.kapita_id_sesi_1)
    if not v_kapita_1:
        raise ServiceException(status_code=404, detail=f"Kapita Sesi 1 dengan ID {p_payload.kapita_id_sesi_1} tidak ditemukan.")

    v_kapita_2 = dao_get_kapita_by_id(p_payload.kapita_id_sesi_2)
    if not v_kapita_2:
        raise ServiceException(status_code=404, detail=f"Kapita Sesi 2 dengan ID {p_payload.kapita_id_sesi_2} tidak ditemukan.")

    v_eff_kuota_1, v_eff_left_1, v_quota_1 = _compute_effective_left(v_participant["pgereja"], p_payload.kapita_id_sesi_1, 1)
    if v_quota_1 is None:
        raise ServiceException(status_code=400, detail=f"Kuota untuk gereja '{v_church['name']}' kapita '{v_kapita_1['namakapita']}' belum diatur.")

    v_eff_kuota_2, v_eff_left_2, v_quota_2 = _compute_effective_left(v_participant["pgereja"], p_payload.kapita_id_sesi_2, 2)
    if v_quota_2 is None:
        raise ServiceException(status_code=400, detail=f"Kuota untuk gereja '{v_church['name']}' kapita '{v_kapita_2['namakapita']}' belum diatur.")

    dao_update_registration(
        p_id=p_reg_id, p_unama=v_participant["pnama"], p_ugereja=v_participant["pgereja"],
        p_kapita_id_sesi_1=p_payload.kapita_id_sesi_1, p_kapita_id_sesi_2=p_payload.kapita_id_sesi_2,
        p_uparticipant=p_payload.uparticipant,
    )
    v_updated = dao_get_registration_by_id(p_reg_id)
    return {
        "id": v_updated["uid"],
        "full_name": v_updated["full_name"],
        "church_gkode": v_updated["church_gkode"], "church_name": v_updated["church_name"],
        "kapita_id_sesi_1": v_updated["kapita_id_sesi_1"], "kapita_name_sesi_1": v_updated["kapita_name_sesi_1"],
        "kapita_id_sesi_2": v_updated["kapita_id_sesi_2"], "kapita_name_sesi_2": v_updated["kapita_name_sesi_2"],
        "uparticipant": v_updated["uparticipant"],
        "registered_at": str(v_updated["registered_at"]),
    }


@validasi
def ctrl_delete_registration(p_reg_id):
    v_reg = dao_get_registration_by_id(p_reg_id)
    if not v_reg:
        raise ServiceException(status_code=404, detail=f"Pendaftaran dengan ID {p_reg_id} tidak ditemukan.")
    return dao_delete_registration(p_reg_id)


# ═══════════════════════════════════════════════════════════════════════════════
# USER
# ═══════════════════════════════════════════════════════════════════════════════

@validasi
def ctrl_create_user(p_payload):
    v_participant = dao_get_participant_by_id(p_payload.uparticipant)
    if not v_participant:
        raise ServiceException(status_code=404, detail=f"Peserta dengan ID {p_payload.uparticipant} tidak ditemukan.")
    if v_participant["pflag"] == "F":
        raise ServiceException(status_code=400, detail=f"Peserta '{v_participant['pnama']}' sudah terdaftar.")

    v_church = dao_get_church_by_gkode(v_participant["pgereja"])
    if not v_church:
        raise ServiceException(status_code=404, detail=f"Gereja dengan kode {v_participant['pgereja']} tidak ditemukan.")

    v_kapita_1 = dao_get_kapita_by_id(p_payload.ukapita_sesi_1)
    if not v_kapita_1:
        raise ServiceException(status_code=404, detail=f"Kapita Sesi 1 dengan ID {p_payload.ukapita_sesi_1} tidak ditemukan.")

    v_kapita_2 = dao_get_kapita_by_id(p_payload.ukapita_sesi_2)
    if not v_kapita_2:
        raise ServiceException(status_code=404, detail=f"Kapita Sesi 2 dengan ID {p_payload.ukapita_sesi_2} tidak ditemukan.")

    v_eff_kuota_1, v_eff_left_1, v_quota_1 = _compute_effective_left(v_participant["pgereja"], p_payload.ukapita_sesi_1, 1)
    if v_quota_1 is None:
        raise ServiceException(status_code=400, detail=f"Kuota untuk gereja '{v_church['name']}' kapita '{v_kapita_1['namakapita']}' belum diatur.")

    v_eff_kuota_2, v_eff_left_2, v_quota_2 = _compute_effective_left(v_participant["pgereja"], p_payload.ukapita_sesi_2, 2)
    if v_quota_2 is None:
        raise ServiceException(status_code=400, detail=f"Kuota untuk gereja '{v_church['name']}' kapita '{v_kapita_2['namakapita']}' belum diatur.")

    if p_payload.ukapita_sesi_1 == p_payload.ukapita_sesi_2:
        if v_eff_left_1 < 1 or v_eff_left_2 < 1:
            raise ServiceException(
                status_code=400,
                detail=f"Kapita '{v_kapita_1['namakapita']}' tidak cukup untuk mendaftar 2 sesi sekaligus (sisa sesi 1: {v_eff_left_1}, sisa sesi 2: {v_eff_left_2})."
            )
    else:
        v_errors = []
        if v_eff_left_1 <= 0:
            v_errors.append(f"Sesi 1 - Kapita '{v_kapita_1['namakapita']}' sudah penuh (kuota: {v_eff_kuota_1}, terdaftar: {v_quota_1['registered_sesi_1']})")
        if v_eff_left_2 <= 0:
            v_errors.append(f"Sesi 2 - Kapita '{v_kapita_2['namakapita']}' sudah penuh (kuota: {v_eff_kuota_2}, terdaftar: {v_quota_2['registered_sesi_2']})")
        if v_errors:
            raise ServiceException(status_code=400, detail="; ".join(v_errors))

    v_create_result = dao_create_user(
        p_unama=v_participant["pnama"], p_ugereja=v_participant["pgereja"],
        p_ukapita_sesi_1=p_payload.ukapita_sesi_1, p_ukapita_sesi_2=p_payload.ukapita_sesi_2,
        p_uparticipant=p_payload.uparticipant,
    )

    if v_create_result["status"] == "F":
        raise ServiceException(status_code=500, detail=v_create_result["message"])
    if not v_create_result["results"] or not isinstance(v_create_result["results"], list):
        raise ServiceException(status_code=500, detail="Gagal mendapatkan id user setelah insert.")

    v_new_id = v_create_result["results"][0]["uid"]
    v_saved = dao_get_user_by_id(v_new_id)
    if not v_saved:
        raise ServiceException(status_code=500, detail="Gagal mengambil data user setelah disimpan.")
    # update Google Sheet if service available
    if update_kapita_for_pid:
        try:
            update_kapita_for_pid(v_saved["uparticipant"], v_saved.get("kapita_name_sesi_1", ""), v_saved.get("kapita_name_sesi_2", ""))
        except Exception:
            pass
    return {
        "uid": v_saved["uid"],
        "full_name": v_saved["unama"],
        "church_gkode": v_saved["ugereja"], "church_name": v_saved["church_name"],
        "ukapita_sesi_1": v_saved["ukapita_sesi_1"], "kapita_name_sesi_1": v_saved["kapita_name_sesi_1"],
        "ukapita_sesi_2": v_saved["ukapita_sesi_2"], "kapita_name_sesi_2": v_saved["kapita_name_sesi_2"],
        "uparticipant": v_saved["uparticipant"],
        "registered_at": str(v_saved["uregistered_at"]),
    }


@validasi
def ctrl_get_all_users():
    return [{
        "uid": v["uid"],
        "full_name": v["unama"],
        "church_gkode": v["ugereja"], "church_name": v["church_name"],
        "ukapita_sesi_1": v["ukapita_sesi_1"], "kapita_name_sesi_1": v["kapita_name_sesi_1"],
        "ukapita_sesi_2": v["ukapita_sesi_2"], "kapita_name_sesi_2": v["kapita_name_sesi_2"],
        "uparticipant": v["uparticipant"],
        "registered_at": str(v["uregistered_at"]),
    } for v in dao_get_all_users()]


@validasi
def ctrl_get_user_by_id(p_uid):
    v_user = dao_get_user_by_id(p_uid)
    if not v_user:
        raise ServiceException(status_code=404, detail=f"User dengan ID {p_uid} tidak ditemukan.")
    return {
        "uid": v_user["uid"],
        "full_name": v_user["unama"],
        "church_gkode": v_user["ugereja"], "church_name": v_user["church_name"],
        "ukapita_sesi_1": v_user["ukapita_sesi_1"], "kapita_name_sesi_1": v_user["kapita_name_sesi_1"],
        "ukapita_sesi_2": v_user["ukapita_sesi_2"], "kapita_name_sesi_2": v_user["kapita_name_sesi_2"],
        "uparticipant": v_user["uparticipant"],
        "registered_at": str(v_user["uregistered_at"]),
    }


@validasi
def ctrl_update_user(p_uid, p_payload):
    v_user = dao_get_user_by_id(p_uid)
    if not v_user:
        raise ServiceException(status_code=404, detail=f"User dengan ID {p_uid} tidak ditemukan.")

    v_participant = dao_get_participant_by_id(p_payload.uparticipant)
    if not v_participant:
        raise ServiceException(status_code=404, detail=f"Peserta dengan ID {p_payload.uparticipant} tidak ditemukan.")
    if v_participant["pflag"] == "F" and v_user["uparticipant"] != p_payload.uparticipant:
        raise ServiceException(status_code=400, detail=f"Peserta '{v_participant['pnama']}' sudah terdaftar.")

    v_church = dao_get_church_by_gkode(v_participant["pgereja"])
    if not v_church:
        raise ServiceException(status_code=404, detail=f"Gereja dengan kode {v_participant['pgereja']} tidak ditemukan.")

    v_kapita_1 = dao_get_kapita_by_id(p_payload.ukapita_sesi_1)
    if not v_kapita_1:
        raise ServiceException(status_code=404, detail=f"Kapita Sesi 1 dengan ID {p_payload.ukapita_sesi_1} tidak ditemukan.")

    v_kapita_2 = dao_get_kapita_by_id(p_payload.ukapita_sesi_2)
    if not v_kapita_2:
        raise ServiceException(status_code=404, detail=f"Kapita Sesi 2 dengan ID {p_payload.ukapita_sesi_2} tidak ditemukan.")

    dao_update_user(
        p_uid=p_uid, p_unama=v_participant["pnama"], p_ugereja=v_participant["pgereja"],
        p_ukapita_sesi_1=p_payload.ukapita_sesi_1, p_ukapita_sesi_2=p_payload.ukapita_sesi_2,
        p_uparticipant=p_payload.uparticipant,
    )
    v_updated = dao_get_user_by_id(p_uid)
    # update Google Sheet if service available
    if update_kapita_for_pid:
        try:
            update_kapita_for_pid(v_updated["uparticipant"], v_updated.get("kapita_name_sesi_1", ""), v_updated.get("kapita_name_sesi_2", ""))
        except Exception:
            pass

    return {
        "uid": v_updated["uid"],
        "full_name": v_updated["unama"],
        "church_gkode": v_updated["ugereja"], "church_name": v_updated["church_name"],
        "ukapita_sesi_1": v_updated["ukapita_sesi_1"], "kapita_name_sesi_1": v_updated["kapita_name_sesi_1"],
        "ukapita_sesi_2": v_updated["ukapita_sesi_2"], "kapita_name_sesi_2": v_updated["kapita_name_sesi_2"],
        "uparticipant": v_updated["uparticipant"],
        "registered_at": str(v_updated["uregistered_at"]),
    }


@validasi
def ctrl_delete_user(p_uid):
    v_user = dao_get_user_by_id(p_uid)
    if not v_user:
        raise ServiceException(status_code=404, detail=f"User dengan ID {p_uid} tidak ditemukan.")
    return dao_delete_user(p_uid)


# ═══════════════════════════════════════════════════════════════════════════════
# PARTICIPANT
# ═══════════════════════════════════════════════════════════════════════════════

@validasi
def ctrl_get_participants_by_church(p_gereja):
    if not p_gereja:
        raise ServiceException(status_code=400, detail="Parameter gereja wajib diisi.")
    return dao_get_participants_by_church(p_gereja)


# ═══════════════════════════════════════════════════════════════════════════════
# CETAK EXCEL
# ═══════════════════════════════════════════════════════════════════════════════

def ctrl_export_excel_peserta(p_pilihan, p_sesi_1=None, p_sesi_2=None, p_gkode=None):
    try:
        p_pilihan = int(p_pilihan)
    except (ValueError, TypeError):
        raise ServiceException(status_code=400, detail="Pilihan cetak excel harus berupa angka (1, 2, 3, atau 4).")

    if p_pilihan not in (1, 2, 3, 4):
        raise ServiceException(status_code=400, detail="Pilihan cetak excel tidak valid. Opsi yang tersedia: 1, 2, 3, atau 4.")

    try:
        from src.others.cetakExcel import generate_excel_peserta
        return generate_excel_peserta(p_pilihan, p_sesi_1, p_sesi_2, p_gkode)
    except ServiceException:
        raise
    except Exception as e:
        raise ServiceException(status_code=500, detail=f"Gagal membuat file Excel: {str(e)}")

