import ast
import os

_env_local_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env.local")

if os.path.isfile(_env_local_path):
    with open(_env_local_path) as _f:
        _content = _f.read().strip()
        if _content.startswith("env = "):
            _content = _content[len("env = "):]
        _env = ast.literal_eval(_content)

    SECRET_KEY   = _env["application"]["secret"]
    APP_STATUS   = _env["application"]["status"]
    APP_SERVER   = _env["application"]["server"]

    DATABASE_URL = _env.get("database", {}).get("url", "")
    DB_HOST      = _env["database"]["host"]
    DB_PORT      = int(_env["database"]["port"])
    DB_USER      = _env["database"]["user"]
    DB_PASSWORD  = _env["database"]["password"]
    DB_NAME      = _env["database"]["name"]
    APP_STATUS = os.environ.get("APP_STATUS", "production")
else:
    SECRET_KEY   = os.environ["SECRET_KEY"]
    APP_STATUS   = os.environ["APP_STATUS"]
    APP_SERVER   = os.environ["APP_SERVER"]

    DATABASE_URL = os.environ.get("DATABASE_URL", "")
    DB_HOST      = os.environ["DB_HOST"]
    DB_PORT      = int(os.environ["DB_PORT"])
    DB_USER      = os.environ["DB_USER"]
    DB_PASSWORD  = os.environ["DB_PASSWORD"]
    DB_NAME      = os.environ["DB_NAME"]
    APP_STATUS = os.environ.get("APP_STATUS", "production")

if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)