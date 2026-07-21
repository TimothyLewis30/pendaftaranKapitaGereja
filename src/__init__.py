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

    return app


app = createApp()
