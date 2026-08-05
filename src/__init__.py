from flask import Flask
from flask_restful import Api
from flask_cors import CORS
from src.utils.exceptions import ServiceException
from src.utils import responseJson
from src.database import close_connection
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
)


import hashlib
import json
import random
import string


def _generate_response_signature(p_secret: str, p_salt: str, p_response):
    v_content_type = p_response.headers.get("Content-Type", "")
    if "application/json" in v_content_type:
        try:
            v_json_data = p_response.get_json()
            if isinstance(v_json_data, (dict, list)):
                v_data = json.dumps(v_json_data, sort_keys=True, separators=(",", ":"))
            else:
                v_data = str(v_json_data)
        except Exception:
            v_data = p_response.get_data(as_text=True)
    else:
        v_data = p_response.get_data().decode("utf-8", errors="ignore")

    v_raw = f"APIKAPITAGKYALSUT{p_secret}{p_salt}{v_data}"
    return hashlib.sha256(v_raw.encode("utf-8")).hexdigest()


def createApp():
    app = Flask(__name__)
    app.config.from_pyfile("settings.py")
    app.config["DEBUG"] = True if app.config["APP_STATUS"] == "DEVELOPMENT" else False
    CORS(app)

    api = Api(app)
    app.teardown_appcontext(close_connection)

    from src.routes import registerRoutes
    registerRoutes(api)

    @app.errorhandler(ServiceException)
    def handle_service_error(e):
        return responseJson(e.status_code, False, e.detail, []), e.status_code

    @app.after_request
    def attach_signature_headers(response):
        v_secret = app.config.get("SECRET_KEY", "")
        v_salt = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
        v_signature = _generate_response_signature(v_secret, v_salt, response)
        response.headers["X-Salt"] = v_salt
        response.headers["X-Signature"] = v_signature
        return response

    return app


app = createApp()

