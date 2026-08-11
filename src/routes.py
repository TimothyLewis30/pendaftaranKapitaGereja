"""
routes.py
Semua routing endpoint (gabungan).
"""
from flask import request, Response
from flask_restful import Resource
from pydantic import ValidationError
from src.controller.modul import (
    ctrl_ping,
    ctrl_admin_login, ctrl_create_admin, ctrl_get_all_admins,
    ctrl_get_admin_by_id, ctrl_update_admin, ctrl_delete_admin,
    ctrl_get_all_churches, ctrl_get_church_detail, ctrl_create_church,
    ctrl_update_church, ctrl_delete_church,
    ctrl_set_church_kapita_quota, ctrl_get_church_kapita_quotas,
    ctrl_get_church_kapita_quota_detail, ctrl_delete_church_kapita_quota,
    ctrl_create_kapita, ctrl_get_all_kapita, ctrl_get_kapita_by_id,
    ctrl_update_kapita, ctrl_delete_kapita,
    ctrl_create_registration, ctrl_get_registration_by_id,
    ctrl_check_registration_by_email, ctrl_update_registration,
    ctrl_delete_registration,
    ctrl_create_user, ctrl_get_all_users, ctrl_get_user_by_id,
    ctrl_update_user, ctrl_delete_user, ctrl_export_excel_peserta,
    ctrl_get_participants_by_church,
)
from src.models.admin_model import AdminCreate, AdminLogin
from src.models.church_model import ChurchCreate, ChurchUpdate, ChurchKapitaQuotaCreate
from src.models.kapita_model import KapitaCreate
from src.models.user_model import RegistrationCreate, UserCreate, CetakExcelRequest
from src.validasi.validate import validasi
from src.utils import responseJson


# ═══════════════════════════════════════════════════════════════════════════════
# ADMIN
# ═══════════════════════════════════════════════════════════════════════════════

class AdminLoginResource(Resource):
    def post(self):
        try:
            v_json = request.get_json() or {}
            v_payload = AdminLogin(**v_json)
        except ValidationError as e:
            return responseJson(400, False, "Validasi data gagal.", e.errors()), 400
        v_result = ctrl_admin_login(v_payload.email, v_payload.password)
        return responseJson(200, True, "Login berhasil.", v_result)


class AdminListResource(Resource):
    def get(self):
        v_data = ctrl_get_all_admins()
        return responseJson(200, True, "Daftar admin berhasil ditemukan.", v_data)

    def post(self):
        try:
            v_json = request.get_json() or {}
            v_payload = AdminCreate(**v_json)
        except ValidationError as e:
            return responseJson(400, False, "Validasi data gagal.", e.errors()), 400
        v_result = ctrl_create_admin(
            v_payload.username, v_payload.email, v_payload.password, v_payload.role)
        return responseJson(201, True, "Admin berhasil disimpan.", v_result), 201


class AdminDetailResource(Resource):
    def get(self, p_aid):
        v_result = ctrl_get_admin_by_id(p_aid)
        return responseJson(200, True, "Detail admin berhasil ditemukan.", v_result)

    def put(self, p_aid):
        try:
            v_json = request.get_json() or {}
            v_payload = AdminCreate(**v_json)
        except ValidationError as e:
            return responseJson(400, False, "Validasi data gagal.", e.errors()), 400
        v_result = ctrl_update_admin(
            p_aid, v_payload.username, v_payload.email, v_payload.password, v_payload.role)
        return responseJson(200, True, "Admin berhasil diupdate.", v_result)

    def delete(self, p_aid):
        ctrl_delete_admin(p_aid)
        return responseJson(200, True, "Admin berhasil dihapus.", [])


# ═══════════════════════════════════════════════════════════════════════════════
# GEREJA
# ═══════════════════════════════════════════════════════════════════════════════

class ChurchListResource(Resource):
    def get(self):
        print("MASUK KEDALAM SINIIIi")
        v_data = ctrl_get_all_churches()
        return responseJson(200, True, "Daftar gereja berhasil ditemukan.", v_data)

    def post(self):
        try:
            v_json = request.get_json() or {}
            v_payload = ChurchCreate(**v_json)
        except ValidationError as e:
            return responseJson(400, False, "Validasi data gagal.", e.errors()), 400
        v_result = ctrl_create_church(v_payload.name)
        return responseJson(201, True, "Gereja berhasil disimpan.", v_result), 201


class ChurchDetailResource(Resource):
    def get(self, p_church_gkode):
        v_church = ctrl_get_church_detail(p_church_gkode)
        return responseJson(200, True, "Detail gereja berhasil ditemukan.", v_church)

    def put(self, p_church_gkode):
        try:
            v_json = request.get_json() or {}
            v_payload = ChurchUpdate(**v_json)
        except ValidationError as e:
            return responseJson(400, False, "Validasi data gagal.", e.errors()), 400
        v_result = ctrl_update_church(p_church_gkode, v_payload.name)
        return responseJson(200, True, "Gereja berhasil diupdate.", v_result)

    def delete(self, p_church_gkode):
        ctrl_delete_church(p_church_gkode)
        return responseJson(200, True, "Gereja berhasil dihapus.", [])


# ═══════════════════════════════════════════════════════════════════════════════
# GEREJA KAPITA QUOTA
# ═══════════════════════════════════════════════════════════════════════════════

class ChurchKapitaQuotaListResource(Resource):
    def get(self, p_church_gkode):
        v_data = ctrl_get_church_kapita_quotas(p_church_gkode)
        return responseJson(200, True, "Daftar kuota kapita gereja berhasil ditemukan.", v_data)

    def post(self, p_church_gkode):
        try:
            v_json = request.get_json() or {}
            v_payload = ChurchKapitaQuotaCreate(**v_json)
        except ValidationError as e:
            return responseJson(400, False, "Validasi data gagal.", e.errors()), 400
        v_result = ctrl_set_church_kapita_quota(
            p_church_gkode, v_payload.kapita_id, v_payload.kuota_sesi_1, v_payload.kuota_sesi_2)
        return responseJson(201, True, "Kuota kapita gereja berhasil disimpan.", v_result), 201


class ChurchKapitaQuotaDetailResource(Resource):
    def get(self, p_church_gkode, p_kapita_id):
        v_result = ctrl_get_church_kapita_quota_detail(
            p_church_gkode, p_kapita_id)
        return responseJson(200, True, "Detail kuota kapita gereja berhasil ditemukan.", v_result)

    def put(self, p_church_gkode, p_kapita_id):
        try:
            v_json = request.get_json() or {}
            v_payload = ChurchKapitaQuotaCreate(**v_json)
        except ValidationError as e:
            return responseJson(400, False, "Validasi data gagal.", e.errors()), 400
        v_result = ctrl_set_church_kapita_quota(
            p_church_gkode, p_kapita_id, v_payload.kuota_sesi_1, v_payload.kuota_sesi_2)
        return responseJson(200, True, "Kuota kapita gereja berhasil diupdate.", v_result)

    def delete(self, p_church_gkode, p_kapita_id):
        ctrl_delete_church_kapita_quota(p_church_gkode, p_kapita_id)
        return responseJson(200, True, "Kuota kapita gereja berhasil dihapus.", [])


# ═══════════════════════════════════════════════════════════════════════════════
# KAPITA
# ═══════════════════════════════════════════════════════════════════════════════

class KapitaListResource(Resource):
    def get(self):
        v_data = ctrl_get_all_kapita()
        return responseJson(200, True, "Daftar kapita berhasil ditemukan.", v_data)

    def post(self):
        try:
            v_json = request.get_json() or {}
            v_payload = KapitaCreate(**v_json)
        except ValidationError as e:
            return responseJson(400, False, "Validasi data gagal.", e.errors()), 400
        v_result = ctrl_create_kapita(v_payload.namakapita)
        return responseJson(201, True, "Kapita berhasil disimpan.", v_result), 201


class KapitaDetailResource(Resource):
    def get(self, p_idkapita):
        v_result = ctrl_get_kapita_by_id(p_idkapita)
        return responseJson(200, True, "Detail kapita berhasil ditemukan.", v_result)

    def put(self, p_idkapita):
        try:
            v_json = request.get_json() or {}
            v_payload = KapitaCreate(**v_json)
        except ValidationError as e:
            return responseJson(400, False, "Validasi data gagal.", e.errors()), 400
        v_result = ctrl_update_kapita(p_idkapita, v_payload.namakapita)
        return responseJson(200, True, "Kapita berhasil diupdate.", v_result)

    def delete(self, p_idkapita):
        ctrl_delete_kapita(p_idkapita)
        return responseJson(200, True, "Kapita berhasil dihapus.", [])


# ═══════════════════════════════════════════════════════════════════════════════
# REGISTRATIONS
# ═══════════════════════════════════════════════════════════════════════════════

class RegistrationListResource(Resource):
    def post(self):
        try:
            v_json = request.get_json() or {}
            v_payload = RegistrationCreate(**v_json)
        except ValidationError as e:
            return responseJson(400, False, "Validasi data gagal.", e.errors()), 400
        v_result = ctrl_create_registration(v_payload)
        return responseJson(201, True, "Pendaftaran berhasil disimpan.", v_result), 201


class RegistrationCheckResource(Resource):
    def get(self, p_email):
        v_result = ctrl_check_registration_by_email(p_email)
        return responseJson(200, True, "Pengecekan email berhasil.", v_result)


class RegistrationDetailResource(Resource):
    def get(self, p_reg_id):
        v_result = ctrl_get_registration_by_id(p_reg_id)
        return responseJson(200, True, "Detail pendaftaran berhasil ditemukan.", v_result)

    def put(self, p_reg_id):
        try:
            v_json = request.get_json() or {}
            v_payload = RegistrationCreate(**v_json)
        except ValidationError as e:
            return responseJson(400, False, "Validasi data gagal.", e.errors()), 400
        v_result = ctrl_update_registration(p_reg_id, v_payload)
        return responseJson(200, True, "Pendaftaran berhasil diupdate.", v_result)

    def delete(self, p_reg_id):
        ctrl_delete_registration(p_reg_id)
        return responseJson(200, True, "Pendaftaran berhasil dihapus.", [])


# ═══════════════════════════════════════════════════════════════════════════════
# USER
# ═══════════════════════════════════════════════════════════════════════════════

class UserListResource(Resource):
    def get(self):
        v_data = ctrl_get_all_users()
        return responseJson(200, True, "Daftar user berhasil ditemukan.", v_data)

    def post(self):
        try:
            v_json = request.get_json() or {}
            v_payload = UserCreate(**v_json)
        except ValidationError as e:
            return responseJson(400, False, "Validasi data gagal.", e.errors()), 400
        v_result = ctrl_create_user(v_payload)
        return responseJson(201, True, "User berhasil disimpan.", v_result), 201


class UserDetailResource(Resource):
    def get(self, p_uid):
        v_result = ctrl_get_user_by_id(p_uid)
        return responseJson(200, True, "Detail user berhasil ditemukan.", v_result)

    def put(self, p_uid):
        try:
            v_json = request.get_json() or {}
            v_payload = UserCreate(**v_json)
        except ValidationError as e:
            return responseJson(400, False, "Validasi data gagal.", e.errors()), 400
        v_result = ctrl_update_user(p_uid, v_payload)
        return responseJson(200, True, "User berhasil diupdate.", v_result)

    def delete(self, p_uid):
        ctrl_delete_user(p_uid)
        return responseJson(200, True, "User berhasil dihapus.", [])


# ═══════════════════════════════════════════════════════════════════════════════
# PING
# ═══════════════════════════════════════════════════════════════════════════════

class PingResource(Resource):
    def get(self):
        try:
            ctrl_ping()
            return responseJson(200, True, "Server is running. DB connected.", [])
        except Exception as e:
            return responseJson(503, False, f"Server is running but DB connection failed: {str(e)}", []), 503


# ═══════════════════════════════════════════════════════════════════════════════
# CETAK EXCEL
# ═══════════════════════════════════════════════════════════════════════════════

class CetakExcelResource(Resource):
    @validasi
    def get(self):
        v_pilihan = request.args.get("pilihan", type=int, default=1)
        v_sesi_1 = request.args.get("sesi_1")
        v_sesi_2 = request.args.get("sesi_2")
        v_gkode = request.args.get("gkode")

        v_excel_bytes, v_filename = ctrl_export_excel_peserta(v_pilihan, v_sesi_1, v_sesi_2, v_gkode)

        return Response(
            v_excel_bytes,
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={v_filename}"}
        )

    @validasi
    def post(self):
        try:
            v_json = request.get_json() or {}
            v_payload = CetakExcelRequest(**v_json)
        except ValidationError as e:
            return responseJson(400, False, "Validasi data gagal.", e.errors()), 400

        v_excel_bytes, v_filename = ctrl_export_excel_peserta(
            v_payload.pilihan, v_payload.sesi_1, v_payload.sesi_2, v_payload.gkode
        )

        return Response(
            v_excel_bytes,
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={v_filename}.xlsx"}
        )


# ═══════════════════════════════════════════════════════════════════════════════
# PARTICIPANT
# ═══════════════════════════════════════════════════════════════════════════════

class ParticipantListByChurchResource(Resource):
    @validasi
    def get(self):
        v_gereja = request.args.get("gereja")
        if not v_gereja:
            return responseJson(400, False, "Parameter 'gereja' wajib diisi.", []), 400
        v_result = ctrl_get_participants_by_church(v_gereja)
        return responseJson(200, True, "Daftar peserta berhasil ditemukan.", v_result)


# ═══════════════════════════════════════════════════════════════════════════════
# REGISTER ROUTES
# ═══════════════════════════════════════════════════════════════════════════════

def registerRoutes(api):
    api.add_resource(PingResource, "/api/ping", endpoint="ping")
    api.add_resource(AdminLoginResource,                "/api/admin/login",                                                 endpoint="admin-login")
    api.add_resource(AdminListResource,                 "/api/admins",                                                      endpoint="admins")
    api.add_resource(AdminDetailResource,               "/api/admins/<int:p_aid>",                                          endpoint="admin-detail")
    api.add_resource(ChurchListResource,                "/api/churches",                                                    endpoint="churches")
    api.add_resource(ChurchDetailResource,              "/api/churches/<string:p_church_gkode>",                            endpoint="church-detail")
    api.add_resource(ChurchKapitaQuotaListResource,     "/api/churches/<string:p_church_gkode>/kapita-quota",              endpoint="church-kapita-quota")
    api.add_resource(ChurchKapitaQuotaDetailResource,   "/api/churches/<string:p_church_gkode>/kapita-quota/<int:p_kapita_id>", endpoint="church-kapita-quota-detail")

    api.add_resource(KapitaListResource,                "/api/kapita",                                                      endpoint="kapita")
    api.add_resource(KapitaDetailResource,              "/api/kapita/<int:p_idkapita>",                                     endpoint="kapita-detail")

    api.add_resource(RegistrationListResource,          "/api/registrations",                                               endpoint="registrations")
    api.add_resource(RegistrationCheckResource,         "/api/registrations/check/<string:p_email>",                        endpoint="registration-check")
    api.add_resource(RegistrationDetailResource,        "/api/registrations/<int:p_reg_id>",                                endpoint="registration-detail")

    api.add_resource(UserListResource,                  "/api/users",                                                       endpoint="users")
    api.add_resource(UserDetailResource,                "/api/users/<int:p_uid>",                                           endpoint="user-detail")

    api.add_resource(CetakExcelResource,                "/api/cetak-excel",                                                 endpoint="cetak-excel")
    api.add_resource(ParticipantListByChurchResource,    "/api/participants",                                                endpoint="participants-by-church")

