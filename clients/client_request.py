"""
Client API Python untuk Pendaftaran Kapita Gereja
Base URL: https://pendaftarankapitagereja.onrender.com

Gunakan:
    response = client.get_churches()
"""

import ast
import hashlib
import json
import os
import random
import string
import requests


BASE_URL = "https://pendaftarankapitagereja.onrender.com"


def _load_env_local(p_filename: str = ".env.local") -> dict:
    v_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), p_filename)
    if not os.path.isfile(v_path):
        return {}
    with open(v_path) as v_f:
        v_content = v_f.read().strip()
        if v_content.startswith("env = "):
            v_content = v_content[len("env = "):]
        return ast.literal_eval(v_content)


class ApiClient:

    def __init__(self, p_secret_key: str, p_base_url: str = None):
        self.v_secret_key = p_secret_key
        self.v_base_url = (p_base_url or BASE_URL).rstrip("/")
        self.v_admin_id = None

    def set_admin(self, p_admin_id: int):
        self.v_admin_id = p_admin_id
        return self

    def _generate_salt(self, p_length: int = 16) -> str:
        v_chars = string.ascii_letters + string.digits
        v_bytes = random.choices(range(len(v_chars)), k=p_length)
        return "".join(v_chars[i] for i in v_bytes)

    def _generate_signature(self, p_salt: str, p_data) -> str:
        v_body = ""
        if isinstance(p_data, (dict, list)):
            v_body = json.dumps(p_data, sort_keys=True, separators=(",", ":"))
        elif isinstance(p_data, (bytes, bytearray)):
            v_body = p_data.decode("utf-8", errors="ignore")
        elif p_data:
            v_body = str(p_data)

        v_raw = f"APIKAPITAGKYALSUT{self.v_secret_key}{p_salt}{v_body}"
        v_result = hashlib.sha256(v_raw.encode("utf-8")).hexdigest()
        print(f"DEBUG: raw={v_raw}, signature={v_result}")
        return v_result

    def _build_headers(self, p_data=None) -> dict:
        v_salt = self._generate_salt()
        v_headers = {
            "X-Signature": self._generate_signature(v_salt, p_data),
            "X-Salt": v_salt,
            "Content-Type": "application/json",
        }
        if self.v_admin_id is not None:
            v_headers["X-Admin-ID"] = str(self.v_admin_id)
        return v_headers

    def _request(self, p_method: str, p_path: str, p_json_body=None, p_params=None) -> dict:
        v_url = f"{self.v_base_url}{p_path}"
        if p_method == "GET" and p_params:
            v_data = p_params
        else:
            v_data = p_json_body or {}

        v_headers = self._build_headers(v_data)

        v_resp = requests.request(
            method=p_method,
            url=v_url,
            json=v_data if p_method != "GET" else None,
            params=p_params if p_method == "GET" else None,
            headers=v_headers,
            timeout=30,
        )
        return v_resp.json()

    # ── Auth ──────────────────────────────────────────────────

    def login(self, p_email: str, p_password: str) -> dict:
        return self._request("POST", "/api/admin/login", p_json_body={
            "email": p_email,
            "password": p_password,
        })

    # ── Admin ─────────────────────────────────────────────────

    def get_admins(self) -> dict:
        return self._request("GET", "/api/admins")

    def get_admin(self, p_admin_id: int) -> dict:
        return self._request("GET", f"/api/admins/{p_admin_id}")

    def create_admin(self, p_username: str, p_email: str, p_password: str, p_role: str = None) -> dict:
        v_body = {"username": p_username, "email": p_email, "password": p_password}
        if p_role:
            v_body["role"] = p_role
        return self._request("POST", "/api/admins", p_json_body=v_body)

    def update_admin(self, p_admin_id: int, p_username: str, p_email: str, p_password: str, p_role: str = None) -> dict:
        v_body = {"username": p_username, "email": p_email, "password": p_password}
        if p_role:
            v_body["role"] = p_role
        return self._request("PUT", f"/api/admins/{p_admin_id}", p_json_body=v_body)

    def delete_admin(self, p_admin_id: int) -> dict:
        return self._request("DELETE", f"/api/admins/{p_admin_id}")

    # ── Church ────────────────────────────────────────────────

    def get_churches(self) -> dict:
        return self._request("GET", "/api/churches")

    def get_church(self, p_gkode: str) -> dict:
        return self._request("GET", f"/api/churches/{p_gkode}")

    def create_church(self, p_name: str) -> dict:
        return self._request("POST", "/api/churches", p_json_body={"name": p_name})

    def update_church(self, p_gkode: str, p_name: str) -> dict:
        return self._request("PUT", f"/api/churches/{p_gkode}", p_json_body={"name": p_name})

    def delete_church(self, p_gkode: str) -> dict:
        return self._request("DELETE", f"/api/churches/{p_gkode}")

    # ── Church Kapita Quota ───────────────────────────────────

    def get_church_kapita_quotas(self, p_gkode: str) -> dict:
        return self._request("GET", f"/api/churches/{p_gkode}/kapita-quota")

    def get_church_kapita_quota(self, p_gkode: str, p_kapita_id: int) -> dict:
        return self._request("GET", f"/api/churches/{p_gkode}/kapita-quota/{p_kapita_id}")

    def set_church_kapita_quota(self, p_gkode: str, p_kapita_id: int, p_kuota: int) -> dict:
        return self._request("POST", f"/api/churches/{p_gkode}/kapita-quota", p_json_body={
            "kapita_id": p_kapita_id,
            "kuota": p_kuota,
        })

    def update_church_kapita_quota(self, p_gkode: str, p_kapita_id: int, p_kuota: int) -> dict:
        return self._request("PUT", f"/api/churches/{p_gkode}/kapita-quota/{p_kapita_id}", p_json_body={
            "kapita_id": p_kapita_id,
            "kuota": p_kuota,
        })

    def delete_church_kapita_quota(self, p_gkode: str, p_kapita_id: int) -> dict:
        return self._request("DELETE", f"/api/churches/{p_gkode}/kapita-quota/{p_kapita_id}")

    # ── Kapita ────────────────────────────────────────────────

    def get_kapita_list(self) -> dict:
        return self._request("GET", "/api/kapita")

    def get_kapita(self, p_kapita_id: int) -> dict:
        return self._request("GET", f"/api/kapita/{p_kapita_id}")

    def create_kapita(self, p_namakapita: str) -> dict:
        return self._request("POST", "/api/kapita", p_json_body={"namakapita": p_namakapita})

    def update_kapita(self, p_kapita_id: int, p_namakapita: str) -> dict:
        return self._request("PUT", f"/api/kapita/{p_kapita_id}", p_json_body={"namakapita": p_namakapita})

    def delete_kapita(self, p_kapita_id: int) -> dict:
        return self._request("DELETE", f"/api/kapita/{p_kapita_id}")

    # ── Registration ──────────────────────────────────────────

    def create_registration(self, p_full_name: str, p_email: str, p_phone: str,
                            p_birth_date: str, p_address: str, p_church_gkode: str,
                            p_kapita_id: int, p_notes: str = None) -> dict:
        v_body = {
            "full_name": p_full_name,
            "email": p_email,
            "phone": p_phone,
            "birth_date": p_birth_date,
            "address": p_address,
            "church_gkode": p_church_gkode,
            "kapita_id": p_kapita_id,
        }
        if p_notes:
            v_body["notes"] = p_notes
        return self._request("POST", "/api/registrations", p_json_body=v_body)

    def check_registration(self, p_email: str) -> dict:
        return self._request("GET", f"/api/registrations/check/{p_email}")

    def get_registration(self, p_reg_id: int) -> dict:
        return self._request("GET", f"/api/registrations/{p_reg_id}")

    def update_registration(self, p_reg_id: int, p_full_name: str, p_email: str, p_phone: str,
                            p_birth_date: str, p_address: str, p_church_gkode: str,
                            p_kapita_id: int, p_notes: str = None) -> dict:
        v_body = {
            "full_name": p_full_name,
            "email": p_email,
            "phone": p_phone,
            "birth_date": p_birth_date,
            "address": p_address,
            "church_gkode": p_church_gkode,
            "kapita_id": p_kapita_id,
        }
        if p_notes:
            v_body["notes"] = p_notes
        return self._request("PUT", f"/api/registrations/{p_reg_id}", p_json_body=v_body)

    def delete_registration(self, p_reg_id: int) -> dict:
        return self._request("DELETE", f"/api/registrations/{p_reg_id}")

    # ── User ──────────────────────────────────────────────────

    def get_users(self) -> dict:
        return self._request("GET", "/api/users")

    def get_user(self, p_uid: int) -> dict:
        return self._request("GET", f"/api/users/{p_uid}")

    def create_user(self, p_full_name: str, p_email: str, p_phone: str,
                    p_birth_date: str, p_address: str, p_church_gkode: str,
                    p_ukapita: int, p_notes: str = None) -> dict:
        v_body = {
            "full_name": p_full_name,
            "email": p_email,
            "phone": p_phone,
            "birth_date": p_birth_date,
            "address": p_address,
            "church_gkode": p_church_gkode,
            "ukapita": p_ukapita,
        }
        if p_notes:
            v_body["notes"] = p_notes
        return self._request("POST", "/api/users", p_json_body=v_body)

    def update_user(self, p_uid: int, p_full_name: str, p_email: str, p_phone: str,
                    p_birth_date: str, p_address: str, p_church_gkode: str,
                    p_ukapita: int, p_notes: str = None) -> dict:
        v_body = {
            "full_name": p_full_name,
            "email": p_email,
            "phone": p_phone,
            "birth_date": p_birth_date,
            "address": p_address,
            "church_gkode": p_church_gkode,
            "ukapita": p_ukapita,
        }
        if p_notes:
            v_body["notes"] = p_notes
        return self._request("PUT", f"/api/users/{p_uid}", p_json_body=v_body)

    def delete_user(self, p_uid: int) -> dict:
        return self._request("DELETE", f"/api/users/{p_uid}")


# ── Contoh Penggunaan ──────────────────────────────────────────
# Endpoint publik (tidak perlu login):
#   - get_churches, get_church, get_kapita_list, get_kapita
#   - create_user, create_registration, check_registration
#   - get_users, get_user, get_registration, dll.
#
# Endpoint admin (perlu login + set_admin):
#   - create/update/delete church, kapita, quota
#   - create/update/delete admin
#   - create/update/delete registration (admin form)
if __name__ == "__main__":
    v_env = _load_env_local()
    v_secret = "ISI DENGAN SECRETMU"  # Ganti dengan secret key yang sesuai
    v_client = ApiClient(p_secret_key=v_secret)

    # ── Publik: tanpa login ──────────────────────────────────
    print("=== Daftar Gereja (publik) ===")
    v_churches = v_client.get_churches()
    print(json.dumps(v_churches, indent=2, ensure_ascii=False))

    print("\n=== Daftar Kapita (publik) ===")
    v_kapita = v_client.get_kapita_list()
    print(json.dumps(v_kapita, indent=2, ensure_ascii=False))

    # ── Publik: daftar user ──────────────────────────────────
    print("\n=== Daftar User (publik) ===")
    v_user_resp = v_client.create_user(
        p_full_name="Yohanes",
        p_email="yohanes@test.com",
        p_phone="08123456789",
        p_birth_date="2000-01-15",
        p_address="Jl. Panjang No. 1",
        p_church_gkode="GKY001",
        p_ukapita=3,
        p_notes="Pemuda",
    )
    print(json.dumps(v_user_resp, indent=2, ensure_ascii=False))

    # ── Admin: login dulu ───────────────────────────────────
    print("\n=== Login Admin ===")
    v_login_resp = v_client.login("superadmin@gereja.com", "superadmin123")
    print(json.dumps(v_login_resp, indent=2, ensure_ascii=False))

    if v_login_resp.get("status"):
        v_admin_id = v_login_resp["results"]["aid"]
        v_client.set_admin(v_admin_id)

        # Hanya endpoint ini yang butuh admin
        print("\n=== Buat Gereja (admin) ===")
        v_new_church = v_client.create_church("Gereja Baru")
        print(json.dumps(v_new_church, indent=2, ensure_ascii=False))
