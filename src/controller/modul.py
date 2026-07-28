"""
controller/modul.py
Business logic untuk semua modul (gabungan).
"""
from src.utils.exceptions import ServiceException
from src.validasi.validate import validasi, require_role
from src.dao.modul import (
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
    dao_get_registration_by_email, dao_count_registrations_by_church_and_kapita,
    dao_update_registration, dao_delete_registration,
    dao_create_user, dao_get_all_users, dao_get_user_by_id,
    dao_update_user, dao_delete_user, dao_count_users_by_church_and_kapita,
)
from werkzeug.security import generate_password_hash, check_password_hash


def _compute_effective_left(p_church_gkode, p_kapita_id):
    v_quota = dao_get_quota_by_church_and_kapita(p_church_gkode, p_kapita_id)
    if not v_quota:
        return None, None, None
    v_total_kapita = len(dao_get_all_kapita())
    v_kuota = v_quota["kuota"]
    if v_kuota < v_total_kapita and v_total_kapita > 0:
        v_effective_kuota = v_kuota * v_total_kapita
    else:
        v_effective_kuota = v_kuota
    v_registered = v_quota["registered"]
    v_effective_left = v_effective_kuota - v_registered
    return v_effective_kuota, v_effective_left, v_quota


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

def _build_church_response(p_church, p_kapita_quotas, p_total_kapita_count):
    v_result_kapita = []
    v_any_kapita_available = False

    for k in p_kapita_quotas:
        v_kuota = k["kuota"]
        v_registered = k["registered"]

        if v_kuota < p_total_kapita_count and p_total_kapita_count > 0:
            v_effective_kuota = v_kuota * p_total_kapita_count
        else:
            v_effective_kuota = v_kuota

        v_effective_left = v_effective_kuota - v_registered
        v_flag_kapita = "T" if v_effective_left > 0 else "F"
        if v_effective_left > 0:
            v_any_kapita_available = True

        v_result_kapita.append({
            "gkid": k["gkid"],
            "gkode": k["gkode"],
            "idkapita": k["idkapita"],
            "kapita_name": k["kapita_name"],
            "kuota": v_kuota,
            "registered": v_registered,
            "quota_left": k["quota_left"],
            "effective_kuota": v_effective_kuota,
            "effective_left": v_effective_left,
            "flag_kapita": v_flag_kapita,
        })

    v_total_effective_quota = sum(k["effective_kuota"] for k in v_result_kapita)
    v_total_registered = sum(k["registered"] for k in v_result_kapita)
    v_flag_gereja = "T" if v_any_kapita_available else "F"

    return {
        "id": p_church["gkode"],
        "name": p_church["name"],
        "total_quota": v_total_effective_quota,
        "total_registered": v_total_registered,
        "quota_left": v_total_effective_quota - v_total_registered,
        "flag_gereja": v_flag_gereja,
        "kapita": v_result_kapita,
    }


@validasi
def ctrl_get_all_churches():
    v_churches = dao_get_all_churches()
    v_total_kapita = len(dao_get_all_kapita())
    v_result = []
    for v_church in v_churches:
        v_kapita_quotas = dao_get_church_kapita_quotas(v_church["gkode"])
        v_result.append(_build_church_response(v_church, v_kapita_quotas, v_total_kapita))
    return v_result


@validasi
def ctrl_get_church_detail(p_church_gkode):
    v_church = dao_get_church_by_gkode(p_church_gkode)
    if not v_church:
        raise ServiceException(status_code=404, detail=f"Gereja dengan kode {p_church_gkode} tidak ditemukan.")
    v_kapita_quotas = dao_get_church_kapita_quotas(p_church_gkode)
    v_total_kapita = len(dao_get_all_kapita())
    return _build_church_response(v_church, v_kapita_quotas, v_total_kapita)


@validasi
@require_role("Admin", "SuperAdmin")
def ctrl_create_church(p_name, **kwargs):
    v_new_gkode = dao_create_church(p_name)
    v_all_kapita = dao_get_all_kapita()
    for v_k in v_all_kapita:
        dao_set_church_kapita_quota(v_new_gkode, v_k["idkapita"], 0)
    v_church = dao_get_church_by_gkode(v_new_gkode)
    v_kapita_quotas = dao_get_church_kapita_quotas(v_new_gkode)
    return _build_church_response(v_church, v_kapita_quotas, len(v_all_kapita))


@validasi
@require_role("Admin", "SuperAdmin")
def ctrl_update_church(p_church_gkode, p_name, **kwargs):
    v_church = dao_get_church_by_gkode(p_church_gkode)
    if not v_church:
        raise ServiceException(status_code=404, detail=f"Gereja dengan kode {p_church_gkode} tidak ditemukan.")
    dao_update_church(p_church_gkode, p_name)
    v_updated = dao_get_church_by_gkode(p_church_gkode)
    v_kapita_quotas = dao_get_church_kapita_quotas(p_church_gkode)
    v_total_kapita = len(dao_get_all_kapita())
    return _build_church_response(v_updated, v_kapita_quotas, v_total_kapita)


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
def ctrl_set_church_kapita_quota(p_church_gkode, p_kapita_id, p_kuota, **kwargs):
    v_church = dao_get_church_by_gkode(p_church_gkode)
    if not v_church:
        raise ServiceException(status_code=404, detail=f"Gereja dengan kode {p_church_gkode} tidak ditemukan.")
    v_kapita = dao_get_kapita_by_id(p_kapita_id)
    if not v_kapita:
        raise ServiceException(status_code=404, detail=f"Kapita dengan ID {p_kapita_id} tidak ditemukan.")
    dao_set_church_kapita_quota(p_church_gkode, p_kapita_id, p_kuota)
    v_quota = dao_get_quota_by_church_and_kapita(p_church_gkode, p_kapita_id)
    v_total_kapita = len(dao_get_all_kapita())
    v_kuota = v_quota["kuota"]
    if v_kuota < v_total_kapita and v_total_kapita > 0:
        v_effective_kuota = v_kuota * v_total_kapita
    else:
        v_effective_kuota = v_kuota
    v_effective_left = v_effective_kuota - v_quota["registered"]
    return {
        "gkid": v_quota["gkid"],
        "gkode": v_quota["gkode"],
        "idkapita": v_quota["idkapita"],
        "kapita_name": v_kapita["namakapita"],
        "kuota": v_kuota,
        "registered": v_quota["registered"],
        "quota_left": v_quota["quota_left"],
        "effective_kuota": v_effective_kuota,
        "effective_left": v_effective_left,
        "flag_kapita": "T" if v_effective_left > 0 else "F",
    }


@validasi
def ctrl_get_church_kapita_quotas(p_church_gkode):
    v_church = dao_get_church_by_gkode(p_church_gkode)
    if not v_church:
        raise ServiceException(status_code=404, detail=f"Gereja dengan kode {p_church_gkode} tidak ditemukan.")
    v_quotas = dao_get_church_kapita_quotas(p_church_gkode)
    v_total_kapita = len(dao_get_all_kapita())
    v_result = []
    v_any_available = False
    for k in v_quotas:
        v_kuota = k["kuota"]
        if v_kuota < v_total_kapita and v_total_kapita > 0:
            v_effective_kuota = v_kuota * v_total_kapita
        else:
            v_effective_kuota = v_kuota
        v_effective_left = v_effective_kuota - k["registered"]
        if v_effective_left > 0:
            v_any_available = True
        v_result.append({
            **k,
            "effective_kuota": v_effective_kuota,
            "effective_left": v_effective_left,
            "flag_kapita": "T" if v_effective_left > 0 else "F",
        })
    return v_result


@validasi
def ctrl_get_church_kapita_quota_detail(p_church_gkode, p_kapita_id):
    v_quota = dao_get_quota_by_church_and_kapita(p_church_gkode, p_kapita_id)
    if not v_quota:
        raise ServiceException(status_code=404, detail=f"Kuota untuk gereja {p_church_gkode} kapita {p_kapita_id} tidak ditemukan.")
    v_kapita = dao_get_kapita_by_id(p_kapita_id)
    v_total_kapita = len(dao_get_all_kapita())
    v_kuota = v_quota["kuota"]
    if v_kuota < v_total_kapita and v_total_kapita > 0:
        v_effective_kuota = v_kuota * v_total_kapita
    else:
        v_effective_kuota = v_kuota
    v_effective_left = v_effective_kuota - v_quota["registered"]
    return {
        "gkid": v_quota["gkid"],
        "gkode": v_quota["gkode"],
        "idkapita": v_quota["idkapita"],
        "kapita_name": v_kapita["namakapita"] if v_kapita else "",
        "kuota": v_kuota,
        "registered": v_quota["registered"],
        "quota_left": v_quota["quota_left"],
        "effective_kuota": v_effective_kuota,
        "effective_left": v_effective_left,
        "flag_kapita": "T" if v_effective_left > 0 else "F",
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
    v_church = dao_get_church_by_gkode(p_payload.church_gkode)
    if not v_church:
        raise ServiceException(status_code=404, detail=f"Gereja dengan kode {p_payload.church_gkode} tidak ditemukan.")

    v_kapita_1 = dao_get_kapita_by_id(p_payload.kapita_id_sesi_1)
    if not v_kapita_1:
        raise ServiceException(status_code=404, detail=f"Kapita Sesi 1 dengan ID {p_payload.kapita_id_sesi_1} tidak ditemukan.")

    v_kapita_2 = dao_get_kapita_by_id(p_payload.kapita_id_sesi_2)
    if not v_kapita_2:
        raise ServiceException(status_code=404, detail=f"Kapita Sesi 2 dengan ID {p_payload.kapita_id_sesi_2} tidak ditemukan.")

    v_eff_kuota_1, v_eff_left_1, v_quota_1 = _compute_effective_left(p_payload.church_gkode, p_payload.kapita_id_sesi_1)
    if v_quota_1 is None:
        raise ServiceException(status_code=400, detail=f"Kuota untuk gereja '{v_church['name']}' kapita '{v_kapita_1['namakapita']}' belum diatur.")

    v_eff_kuota_2, v_eff_left_2, v_quota_2 = _compute_effective_left(p_payload.church_gkode, p_payload.kapita_id_sesi_2)
    if v_quota_2 is None:
        raise ServiceException(status_code=400, detail=f"Kuota untuk gereja '{v_church['name']}' kapita '{v_kapita_2['namakapita']}' belum diatur.")

    v_errors = []
    if v_eff_left_1 <= 0:
        v_errors.append(f"Sesi 1 - Kapita '{v_kapita_1['namakapita']}' sudah penuh (kuota: {v_eff_kuota_1}, terdaftar: {v_quota_1['registered']})")
    if v_eff_left_2 <= 0:
        v_errors.append(f"Sesi 2 - Kapita '{v_kapita_2['namakapita']}' sudah penuh (kuota: {v_eff_kuota_2}, terdaftar: {v_quota_2['registered']})")
    if v_errors:
        raise ServiceException(status_code=400, detail="; ".join(v_errors))

    v_existing = dao_get_registration_by_email(p_payload.email)
    if v_existing:
        raise ServiceException(status_code=409, detail=f"Email '{p_payload.email}' sudah terdaftar.")

    v_new_id = dao_create_user(
        p_full_name=p_payload.full_name, p_email=p_payload.email,
        p_phone=p_payload.phone, p_church_gkode=p_payload.church_gkode,
        p_kapita_id_sesi_1=p_payload.kapita_id_sesi_1, p_kapita_id_sesi_2=p_payload.kapita_id_sesi_2,
    )
    v_saved = dao_get_registration_by_id(v_new_id)

    return {
        "id": v_saved["id"],
        "full_name": v_saved["full_name"], "email": v_saved["email"],
        "phone": v_saved["phone"],
        "church_gkode": v_saved["church_gkode"], "church_name": v_saved["church_name"],
        "kapita_id_sesi_1": v_saved["kapita_id_sesi_1"], "kapita_name_sesi_1": v_saved["kapita_name_sesi_1"],
        "kapita_id_sesi_2": v_saved["kapita_id_sesi_2"], "kapita_name_sesi_2": v_saved["kapita_name_sesi_2"],
        "registered_at": str(v_saved["registered_at"]),
    }


@validasi
def ctrl_get_registration_by_id(p_reg_id):
    v_reg = dao_get_registration_by_id(p_reg_id)
    if not v_reg:
        raise ServiceException(status_code=404, detail=f"Pendaftaran dengan ID {p_reg_id} tidak ditemukan.")
    return {
        "id": v_reg["id"],
        "full_name": v_reg["full_name"], "email": v_reg["email"],
        "phone": v_reg["phone"],
        "church_gkode": v_reg["church_gkode"], "church_name": v_reg["church_name"],
        "kapita_id_sesi_1": v_reg["kapita_id_sesi_1"], "kapita_name_sesi_1": v_reg["kapita_name_sesi_1"],
        "kapita_id_sesi_2": v_reg["kapita_id_sesi_2"], "kapita_name_sesi_2": v_reg["kapita_name_sesi_2"],
        "registered_at": str(v_reg["registered_at"]),
    }


@validasi
def ctrl_check_registration_by_email(p_email):
    v_reg = dao_get_registration_by_email(p_email)
    if v_reg:
        return {"email": p_email, "is_registered": True, "message": f"Email '{p_email}' sudah terdaftar atas nama {v_reg['full_name']}."}
    return {"email": p_email, "is_registered": False, "message": f"Email '{p_email}' belum terdaftar."}


@validasi
def ctrl_update_registration(p_reg_id, p_payload):
    v_reg = dao_get_registration_by_id(p_reg_id)
    if not v_reg:
        raise ServiceException(status_code=404, detail=f"Pendaftaran dengan ID {p_reg_id} tidak ditemukan.")

    v_existing = dao_get_registration_by_email(p_payload.email)
    if v_existing and v_existing["id"] != p_reg_id:
        raise ServiceException(status_code=409, detail=f"Email '{p_payload.email}' sudah terdaftar di pendaftaran lain.")

    dao_update_registration(
        p_id=p_reg_id, p_full_name=p_payload.full_name, p_email=p_payload.email,
        p_phone=p_payload.phone, p_church_gkode=p_payload.church_gkode,
        p_kapita_id_sesi_1=p_payload.kapita_id_sesi_1, p_kapita_id_sesi_2=p_payload.kapita_id_sesi_2,
    )
    v_updated = dao_get_registration_by_id(p_reg_id)
    return {
        "id": v_updated["id"],
        "full_name": v_updated["full_name"], "email": v_updated["email"],
        "phone": v_updated["phone"],
        "church_gkode": v_updated["church_gkode"], "church_name": v_updated["church_name"],
        "kapita_id_sesi_1": v_updated["kapita_id_sesi_1"], "kapita_name_sesi_1": v_updated["kapita_name_sesi_1"],
        "kapita_id_sesi_2": v_updated["kapita_id_sesi_2"], "kapita_name_sesi_2": v_updated["kapita_name_sesi_2"],
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
    v_church = dao_get_church_by_gkode(p_payload.church_gkode)
    if not v_church:
        raise ServiceException(status_code=404, detail=f"Gereja dengan kode {p_payload.church_gkode} tidak ditemukan.")

    v_kapita_1 = dao_get_kapita_by_id(p_payload.ukapita_sesi_1)
    if not v_kapita_1:
        raise ServiceException(status_code=404, detail=f"Kapita Sesi 1 dengan ID {p_payload.ukapita_sesi_1} tidak ditemukan.")

    v_kapita_2 = dao_get_kapita_by_id(p_payload.ukapita_sesi_2)
    if not v_kapita_2:
        raise ServiceException(status_code=404, detail=f"Kapita Sesi 2 dengan ID {p_payload.ukapita_sesi_2} tidak ditemukan.")

    v_eff_kuota_1, v_eff_left_1, v_quota_1 = _compute_effective_left(p_payload.church_gkode, p_payload.ukapita_sesi_1)
    if v_quota_1 is None:
        raise ServiceException(status_code=400, detail=f"Kuota untuk gereja '{v_church['name']}' kapita '{v_kapita_1['namakapita']}' belum diatur.")

    v_eff_kuota_2, v_eff_left_2, v_quota_2 = _compute_effective_left(p_payload.church_gkode, p_payload.ukapita_sesi_2)
    if v_quota_2 is None:
        raise ServiceException(status_code=400, detail=f"Kuota untuk gereja '{v_church['name']}' kapita '{v_kapita_2['namakapita']}' belum diatur.")

    v_errors = []
    if v_eff_left_1 <= 0:
        v_errors.append(f"Sesi 1 - Kapita '{v_kapita_1['namakapita']}' sudah penuh (kuota: {v_eff_kuota_1}, terdaftar: {v_quota_1['registered']})")
    if v_eff_left_2 <= 0:
        v_errors.append(f"Sesi 2 - Kapita '{v_kapita_2['namakapita']}' sudah penuh (kuota: {v_eff_kuota_2}, terdaftar: {v_quota_2['registered']})")
    if v_errors:
        raise ServiceException(status_code=400, detail="; ".join(v_errors))

    v_new_id = dao_create_user(
        p_full_name=p_payload.full_name, p_email=p_payload.email,
        p_phone=p_payload.phone, p_church_gkode=p_payload.church_gkode,
        p_ukapita_sesi_1=p_payload.ukapita_sesi_1, p_ukapita_sesi_2=p_payload.ukapita_sesi_2,
    )
    v_saved = dao_get_user_by_id(v_new_id)
    return {
        "uid": v_saved["uid"],
        "full_name": v_saved["unama"], "email": v_saved["uemail"],
        "phone": v_saved["uphone"],
        "church_gkode": v_saved["ugereja"], "church_name": v_saved["church_name"],
        "ukapita_sesi_1": v_saved["ukapita_sesi_1"], "kapita_name_sesi_1": v_saved["kapita_name_sesi_1"],
        "ukapita_sesi_2": v_saved["ukapita_sesi_2"], "kapita_name_sesi_2": v_saved["kapita_name_sesi_2"],
        "registered_at": str(v_saved["uregistered_at"]),
    }


@validasi
def ctrl_get_all_users():
    return [{
        "uid": v["uid"],
        "full_name": v["unama"], "email": v["uemail"],
        "phone": v["uphone"],
        "church_gkode": v["ugereja"], "church_name": v["church_name"],
        "ukapita_sesi_1": v["ukapita_sesi_1"], "kapita_name_sesi_1": v["kapita_name_sesi_1"],
        "ukapita_sesi_2": v["ukapita_sesi_2"], "kapita_name_sesi_2": v["kapita_name_sesi_2"],
        "registered_at": str(v["uregistered_at"]),
    } for v in dao_get_all_users()]


@validasi
def ctrl_get_user_by_id(p_uid):
    v_user = dao_get_user_by_id(p_uid)
    if not v_user:
        raise ServiceException(status_code=404, detail=f"User dengan ID {p_uid} tidak ditemukan.")
    return {
        "uid": v_user["uid"],
        "full_name": v_user["unama"], "email": v_user["uemail"],
        "phone": v_user["uphone"],
        "church_gkode": v_user["ugereja"], "church_name": v_user["church_name"],
        "ukapita_sesi_1": v_user["ukapita_sesi_1"], "kapita_name_sesi_1": v_user["kapita_name_sesi_1"],
        "ukapita_sesi_2": v_user["ukapita_sesi_2"], "kapita_name_sesi_2": v_user["kapita_name_sesi_2"],
        "registered_at": str(v_user["uregistered_at"]),
    }


@validasi
def ctrl_update_user(p_uid, p_payload):
    v_user = dao_get_user_by_id(p_uid)
    if not v_user:
        raise ServiceException(status_code=404, detail=f"User dengan ID {p_uid} tidak ditemukan.")

    v_church = dao_get_church_by_gkode(p_payload.church_gkode)
    if not v_church:
        raise ServiceException(status_code=404, detail=f"Gereja dengan kode {p_payload.church_gkode} tidak ditemukan.")

    dao_update_user(
        p_uid=p_uid, p_full_name=p_payload.full_name, p_email=p_payload.email,
        p_phone=p_payload.phone, p_church_gkode=p_payload.church_gkode,
        p_ukapita_sesi_1=p_payload.ukapita_sesi_1, p_ukapita_sesi_2=p_payload.ukapita_sesi_2,
    )
    v_updated = dao_get_user_by_id(p_uid)
    return {
        "uid": v_updated["uid"],
        "full_name": v_updated["unama"], "email": v_updated["uemail"],
        "phone": v_updated["uphone"],
        "church_gkode": v_updated["ugereja"], "church_name": v_updated["church_name"],
        "ukapita_sesi_1": v_updated["ukapita_sesi_1"], "kapita_name_sesi_1": v_updated["kapita_name_sesi_1"],
        "ukapita_sesi_2": v_updated["ukapita_sesi_2"], "kapita_name_sesi_2": v_updated["kapita_name_sesi_2"],
        "registered_at": str(v_updated["uregistered_at"]),
    }


@validasi
def ctrl_delete_user(p_uid):
    v_user = dao_get_user_by_id(p_uid)
    if not v_user:
        raise ServiceException(status_code=404, detail=f"User dengan ID {p_uid} tidak ditemukan.")
    return dao_delete_user(p_uid)
