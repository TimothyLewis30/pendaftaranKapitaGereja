import ast
import os

_env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env.local")
with open(_env_path) as _f:
    v_env = ast.literal_eval(_f.read().strip().removeprefix("env = "))

SECRET_KEY = v_env["application"]["secret"]
APP_STATUS = v_env["application"]["status"]
APP_SERVER = v_env["application"]["server"]

DB_HOST = v_env["db"]["host"]
DB_PORT = v_env["db"]["port"]
DB_USER = v_env["db"]["user"]
DB_PASSWORD = v_env["db"]["password"]
DB_NAME = v_env["db"]["name"]
