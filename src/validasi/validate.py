from flask import request, g, make_response, jsonify
from src.utils import responseJson
from src.utils.exceptions import ServiceException
from functools import wraps
from datetime import datetime
import hashlib, json, pytz, traceback


def _generateSignature(p_secret: str, p_salt: str, p_data) -> str:
    if isinstance(p_data, (dict, list)):
        v_data = json.dumps(p_data, sort_keys=True, separators=(",", ":"))
    elif isinstance(p_data, (bytes, bytearray)):
        v_data = p_data.decode("utf-8", errors="ignore")
    else:
        v_data = str(p_data)

        v_raw = f"APIKAPITAGKYALSUT{p_secret}{p_salt}{v_data}"
        v_result = hashlib.sha256(v_raw.encode("utf-8")).hexdigest()
        print(f"DEBUG: raw={v_raw}, signature={v_result}")
        return v_result


def validasi(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        from src import app
        v_secret = app.config["SECRET_KEY"]
        v_signature = request.headers.get("X-Signature")
        v_salt = request.headers.get("X-Salt")

        if not v_signature or not v_salt:
            raise ServiceException(
                status_code=401, detail="Unauthorized: Invalid or missing request API key")

        if request.method == "GET":
            v_data = request.args.to_dict(flat=True)
        elif request.content_type and request.content_type.startswith("multipart/form-data"):
            v_data = request.form.to_dict(flat=True)
        else:
            v_data = request.get_json(silent=True) or {}

        v_expected = _generateSignature(v_secret, v_salt, v_data)
        print("v_expected : ", v_expected)
        if v_signature != v_expected:
            raise ServiceException(
                status_code=401, detail="Unauthorized: Invalid request signature")

        try:
            v_response = fn(*args, **kwargs)
        except Exception as e:
            traceback.print_exc()
            raise ServiceException(
                status_code=500, detail=f"Server Error: {str(e)}")

        return v_response

    return wrapper


def require_role(*p_allowed_roles):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            v_admin_id = request.headers.get("X-Admin-ID")
            if not v_admin_id:
                return responseJson(403, False, "Forbidden: Header X-Admin-ID diperlukan.", []), 403

            try:
                v_admin_id = int(v_admin_id)
            except (ValueError, TypeError):
                return responseJson(400, False, "Bad Request: X-Admin-ID harus berupa angka.", []), 400

            from src.dao.modul import dao_get_admin_by_id
            v_admin = dao_get_admin_by_id(v_admin_id)
            if not v_admin:
                return responseJson(404, False, "NotFound: Admin tidak ditemukan.", []), 404

            v_role = v_admin.get("arole")

            if v_role is None:
                return responseJson(403, False, "Forbidden: Role anda tidak memiliki akses.", []), 403

            if v_role not in p_allowed_roles:
                return responseJson(403, False, f"Forbidden: Role '{v_role}' tidak memiliki akses untuk operasi ini.", []), 403

            kwargs["admin_role"] = v_role
            kwargs["admin_id"] = v_admin_id
            return fn(*args, **kwargs)

        return wrapper
    return decorator
