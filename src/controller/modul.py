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
    v_total_quota = sum(k["kuota"] for k in p_kapita_quotas)
    v_total_registered = sum(k["registered"] for k in p_kapita_quotas)
    return {
        "id": p_church["gkode"],
        "name": p_church["name"],
        "total_quota": v_total_quota,
        "total_registered": v_total_registered,
        "quota_left": v_total_quota - v_total_registered,
        "kapita": p_kapita_quotas,
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
    v_church = dao_get_church_by_gkode(v_new_gkode)
    return _build_church_response(v_church, [])


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
def ctrl_set_church_kapita_quota(p_church_gkode, p_kapita_id, p_kuota, **kwargs):
    v_church = dao_get_church_by_gkode(p_church_gkode)
    if not v_church:
        raise ServiceException(status_code=404, detail=f"Gereja dengan kode {p_church_gkode} tidak ditemukan.")
    v_kapita = dao_get_kapita_by_id(p_kapita_id)
    if not v_kapita:
        raise ServiceException(status_code=404, detail=f"Kapita dengan ID {p_kapita_id} tidak ditemukan.")
    dao_set_church_kapita_quota(p_church_gkode, p_kapita_id, p_kuota)
    v_quota = dao_get_quota_by_church_and_kapita(p_church_gkode, p_kapita_id)
    return {
        "gkid": v_quota["gkid"],
        "gkode": v_quota["gkode"],
        "idkapita": v_quota["idkapita"],
        "kapita_name": v_kapita["namakapita"],
        "kuota": v_quota["kuota"],
        "registered": v_quota["registered"],
        "quota_left": v_quota["quota_left"],
    }


@validasi
def ctrl_get_church_kapita_quotas(p_church_gkode):
    v_church = dao_get_church_by_gkode(p_church_gkode)
    if not v_church:
        raise ServiceException(status_code=404, detail=f"Gereja dengan kode {p_church_gkode} tidak ditemukan.")
    return dao_get_church_kapita_quotas(p_church_gkode)


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
        "kuota": v_quota["kuota"],
        "registered": v_quota["registered"],
        "quota_left": v_quota["quota_left"],
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

    v_kapita = dao_get_kapita_by_id(p_payload.kapita_id)
    if not v_kapita:
        raise ServiceException(status_code=404, detail=f"Kapita dengan ID {p_payload.kapita_id} tidak ditemukan.")

    v_quota = dao_get_quota_by_church_and_kapita(p_payload.church_gkode, p_payload.kapita_id)
    if not v_quota:
        raise ServiceException(status_code=400, detail=f"Kuota untuk gereja '{v_church['name']}' kapita '{v_kapita['namakapita']}' belum diatur.")

    v_registered = dao_count_registrations_by_church_and_kapita(p_payload.church_gkode, p_payload.kapita_id)
    v_quota_left = v_quota["kuota"] - v_registered
    if v_quota_left <= 0:
        raise ServiceException(
            status_code=400,
            detail=f"Kuota untuk gereja '{v_church['name']}' kapita '{v_kapita['namakapita']}' sudah penuh. Total kuota: {v_quota['kuota']} peserta."
        )

    v_existing = dao_get_registration_by_email(p_payload.email)
    if v_existing:
        raise ServiceException(status_code=409, detail=f"Email '{p_payload.email}' sudah terdaftar.")

    v_new_id = dao_create_registration(
        p_full_name=p_payload.full_name, p_email=p_payload.email,
        p_phone=p_payload.phone, p_birth_date=p_payload.birth_date,
        p_address=p_payload.address, p_church_gkode=p_payload.church_gkode,
        p_kapita_id=p_payload.kapita_id, p_notes=p_payload.notes,
    )
    v_saved = dao_get_registration_by_id(v_new_id)

    return {
        "id": v_saved["id"], "full_name": v_saved["full_name"], "email": v_saved["email"],
        "phone": v_saved["phone"], "birth_date": v_saved["birth_date"], "address": v_saved["address"],
        "church_gkode": v_saved["church_gkode"], "church_name": v_saved["church_name"],
        "kapita_id": v_saved["kapita_id"], "kapita_name": v_saved["kapita_name"],
        "notes": v_saved["notes"], "registered_at": str(v_saved["registered_at"]),
    }


@validasi
def ctrl_get_registration_by_id(p_reg_id):
    v_reg = dao_get_registration_by_id(p_reg_id)
    if not v_reg:
        raise ServiceException(status_code=404, detail=f"Pendaftaran dengan ID {p_reg_id} tidak ditemukan.")
    return {
        "id": v_reg["id"], "full_name": v_reg["full_name"], "email": v_reg["email"],
        "phone": v_reg["phone"], "birth_date": v_reg["birth_date"], "address": v_reg["address"],
        "church_gkode": v_reg["church_gkode"], "church_name": v_reg["church_name"],
        "kapita_id": v_reg["kapita_id"], "kapita_name": v_reg["kapita_name"],
        "notes": v_reg["notes"], "registered_at": str(v_reg["registered_at"]),
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
        p_phone=p_payload.phone, p_birth_date=p_payload.birth_date,
        p_address=p_payload.address, p_church_gkode=p_payload.church_gkode,
        p_kapita_id=p_payload.kapita_id, p_notes=p_payload.notes,
    )
    v_updated = dao_get_registration_by_id(p_reg_id)
    return {
        "id": v_updated["id"], "full_name": v_updated["full_name"], "email": v_updated["email"],
        "phone": v_updated["phone"], "birth_date": v_updated["birth_date"], "address": v_updated["address"],
        "church_gkode": v_updated["church_gkode"], "church_name": v_updated["church_name"],
        "kapita_id": v_updated["kapita_id"], "kapita_name": v_updated["kapita_name"],
        "notes": v_updated["notes"], "registered_at": str(v_updated["registered_at"]),
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

    v_kapita = dao_get_kapita_by_id(p_payload.ukapita)
    if not v_kapita:
        raise ServiceException(status_code=404, detail=f"Kapita dengan ID {p_payload.ukapita} tidak ditemukan.")

    v_quota = dao_get_quota_by_church_and_kapita(p_payload.church_gkode, p_payload.ukapita)
    if not v_quota:
        raise ServiceException(status_code=400, detail=f"Kuota untuk gereja '{v_church['name']}' kapita '{v_kapita['namakapita']}' belum diatur.")

    v_registered = dao_count_users_by_church_and_kapita(p_payload.church_gkode, p_payload.ukapita)
    v_quota_left = v_quota["kuota"] - v_registered
    if v_quota_left <= 0:
        raise ServiceException(
            status_code=400,
            detail=f"Kuota untuk gereja '{v_church['name']}' kapita '{v_kapita['namakapita']}' sudah penuh."
        )

    v_new_id = dao_create_user(
        p_full_name=p_payload.full_name, p_email=p_payload.email,
        p_phone=p_payload.phone, p_birth_date=p_payload.birth_date,
        p_address=p_payload.address, p_church_gkode=p_payload.church_gkode,
        p_ukapita=p_payload.ukapita, p_notes=p_payload.notes,
    )
    v_saved = dao_get_user_by_id(v_new_id)
    return {
        "uid": v_saved["uid"], "full_name": v_saved["unama"], "email": v_saved["uemail"],
        "phone": v_saved["uphone"], "birth_date": str(v_saved["ubirth_date"]),
        "address": v_saved["uaddress"], "church_gkode": v_saved["ugereja"],
        "church_name": v_saved["church_name"], "ukapita": v_saved["ukapita"],
        "kapita_name": v_saved["kapita_name"], "notes": v_saved["unotes"],
        "registered_at": str(v_saved["uregistered_at"]),
    }


@validasi
def ctrl_get_all_users():
    return [{
        "uid": v["uid"], "full_name": v["unama"], "email": v["uemail"],
        "phone": v["uphone"], "birth_date": str(v["ubirth_date"]),
        "address": v["uaddress"], "church_gkode": v["ugereja"],
        "church_name": v["church_name"], "ukapita": v["ukapita"],
        "kapita_name": v["kapita_name"], "notes": v["unotes"],
        "registered_at": str(v["uregistered_at"]),
    } for v in dao_get_all_users()]


@validasi
def ctrl_get_user_by_id(p_uid):
    v_user = dao_get_user_by_id(p_uid)
    if not v_user:
        raise ServiceException(status_code=404, detail=f"User dengan ID {p_uid} tidak ditemukan.")
    return {
        "uid": v_user["uid"], "full_name": v_user["unama"], "email": v_user["uemail"],
        "phone": v_user["uphone"], "birth_date": str(v_user["ubirth_date"]),
        "address": v_user["uaddress"], "church_gkode": v_user["ugereja"],
        "church_name": v_user["church_name"], "ukapita": v_user["ukapita"],
        "kapita_name": v_user["kapita_name"], "notes": v_user["unotes"],
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
        p_phone=p_payload.phone, p_birth_date=p_payload.birth_date,
        p_address=p_payload.address, p_church_gkode=p_payload.church_gkode,
        p_ukapita=p_payload.ukapita, p_notes=p_payload.notes,
    )
    v_updated = dao_get_user_by_id(p_uid)
    return {
        "uid": v_updated["uid"], "full_name": v_updated["unama"], "email": v_updated["uemail"],
        "phone": v_updated["uphone"], "birth_date": str(v_updated["ubirth_date"]),
        "address": v_updated["uaddress"], "church_gkode": v_updated["ugereja"],
        "church_name": v_updated["church_name"], "ukapita": v_updated["ukapita"],
        "kapita_name": v_updated["kapita_name"], "notes": v_updated["unotes"],
        "registered_at": str(v_updated["uregistered_at"]),
    }


@validasi
def ctrl_delete_user(p_uid):
    v_user = dao_get_user_by_id(p_uid)
    if not v_user:
        raise ServiceException(status_code=404, detail=f"User dengan ID {p_uid} tidak ditemukan.")
    return dao_delete_user(p_uid)
