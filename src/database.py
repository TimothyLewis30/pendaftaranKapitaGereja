import psycopg2
import psycopg2.extras
from flask import g


def get_connection():
    if 'db' not in g:
        from src import app
        v_url = app.config.get("DATABASE_URL")
        if v_url:
            g.db = psycopg2.connect(v_url, cursor_factory=psycopg2.extras.RealDictCursor)
        else:
            g.db = psycopg2.connect(
                host=app.config["DB_HOST"],
                port=app.config["DB_PORT"],
                dbname=app.config["DB_NAME"],
                user=app.config["DB_USER"],
                password=app.config["DB_PASSWORD"],
                cursor_factory=psycopg2.extras.RealDictCursor,
            )
    return g.db


def close_connection(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()


def seed_superadmin():
    from werkzeug.security import generate_password_hash
    from src import app

    v_url = app.config.get("DATABASE_URL")
    if v_url:
        v_conn = psycopg2.connect(v_url, cursor_factory=psycopg2.extras.RealDictCursor)
    else:
        v_conn = psycopg2.connect(
            host=app.config["DB_HOST"],
            port=app.config["DB_PORT"],
            dbname=app.config["DB_NAME"],
            user=app.config["DB_USER"],
            password=app.config["DB_PASSWORD"],
            cursor_factory=psycopg2.extras.RealDictCursor,
        )
    v_cursor = v_conn.cursor()

    v_cursor.execute('SELECT COUNT(*) AS cnt FROM admin')
    v_row = v_cursor.fetchone()

    if v_row["cnt"] == 0:
        v_hash = generate_password_hash("superadmin123")
        v_cursor.execute(
            'INSERT INTO admin (ausername, aemail, apassword, arole) VALUES (%s, %s, %s, %s)',
            ("superadmin", "superadmin@gereja.com", v_hash, "SuperAdmin")
        )
        v_conn.commit()
        print("[DB] SuperAdmin default dibuat: superadmin@gereja.com / superadmin123")

    v_cursor.close()
    v_conn.close()
