import ast
import os

# ═══════════════════════════════════════════════════════════════════════════════
# Coba baca dari .env.local (development) — format dict lama
# Kalau tidak ada, fallback ke environment variables (Render / production)
# ═══════════════════════════════════════════════════════════════════════════════

_env_local_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env.local")

if os.path.isfile(_env_local_path):
    with open(_env_local_path) as _f:
        _content = _f.read().strip()
        if _content.startswith("env = "):
            _content = _content[len("env = "):]
        _env = ast.literal_eval(_content)

    SECRET_KEY   = _env.get("application", {}).get("secret", "GKYALSUT123")
    APP_STATUS   = _env.get("application", {}).get("status", "DEVELOPMENT")
    APP_SERVER   = _env.get("application", {}).get("server", "LOCAL")

    DATABASE_URL = _env.get("database", {}).get("url", "")
    DB_HOST      = _env.get("database", {}).get("host", "127.0.0.1")
    DB_PORT      = int(_env.get("database", {}).get("port", 5432))
    DB_USER      = _env.get("database", {}).get("user", "postgres")
    DB_PASSWORD  = _env.get("database", {}).get("password", "")
    DB_NAME      = _env.get("database", {}).get("name", "postgres")
else:
    SECRET_KEY   = os.environ.get("SECRET_KEY", "GKYALSUT123")
    APP_STATUS   = os.environ.get("APP_STATUS", "DEVELOPMENT")
    APP_SERVER   = os.environ.get("APP_SERVER", "LOCAL")

    DATABASE_URL = os.environ.get("DATABASE_URL", "")
    DB_HOST      = os.environ.get("DB_HOST", "127.0.0.1")
    DB_PORT      = int(os.environ.get("DB_PORT", 5432))
    DB_USER      = os.environ.get("DB_USER", "postgres")
    DB_PASSWORD  = os.environ.get("DB_PASSWORD", "")
    DB_NAME      = os.environ.get("DB_NAME", "postgres")

# Supabase kadang kasih URL dengan prefix "postgres://", psycopg2 butuh "postgresql://"
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
