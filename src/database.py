import pymysql
from flask import g


def get_connection():
    if 'db' not in g:
        from src import app
        g.db = pymysql.connect(
            host=app.config["DB_HOST"],
            port=app.config["DB_PORT"],
            user=app.config["DB_USER"],
            password=app.config["DB_PASSWORD"],
            database=app.config["DB_NAME"],
            cursorclass=pymysql.cursors.DictCursor,
        )
    return g.db


def close_connection(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_db():
    from src import app
    v_conn = pymysql.connect(
        host=app.config["DB_HOST"],
        port=app.config["DB_PORT"],
        user=app.config["DB_USER"],
        password=app.config["DB_PASSWORD"],
        database=app.config["DB_NAME"],
        cursorclass=pymysql.cursors.DictCursor,
    )
    v_cursor = v_conn.cursor()

    # ── Tabel gereja ──────────────────────────────────────────────────────────
    v_cursor.execute("""
        CREATE TABLE IF NOT EXISTS gereja (
            gkode   VARCHAR(10) NOT NULL PRIMARY KEY,
            gnama   VARCHAR(255) NOT NULL
        )
    """)

    # ── Tabel kapita ──────────────────────────────────────────────────────────
    v_cursor.execute("""
        CREATE TABLE IF NOT EXISTS kapita (
            idkapita    INT AUTO_INCREMENT PRIMARY KEY,
            namakapita  VARCHAR(20) NOT NULL
        )
    """)

    # ── Tabel gereja_kapita (kuota per gereja per KAPITA) ────────────────────
    v_cursor.execute("""
        CREATE TABLE IF NOT EXISTS gereja_kapita (
            gkid        INT AUTO_INCREMENT PRIMARY KEY,
            gkode       VARCHAR(10) NOT NULL,
            idkapita    INT NOT NULL,
            kuota       INT NOT NULL DEFAULT 0,
            FOREIGN KEY (gkode) REFERENCES gereja(gkode),
            FOREIGN KEY (idkapita) REFERENCES kapita(idkapita),
            UNIQUE KEY uq_gereja_kapita (gkode, idkapita)
        )
    """)

    # ── Tabel user ────────────────────────────────────────────────────────────
    v_cursor.execute("""
        CREATE TABLE IF NOT EXISTS user (
            uid             INT AUTO_INCREMENT PRIMARY KEY,
            unama           VARCHAR(100) NOT NULL,
            ugereja         VARCHAR(10) NOT NULL,
            ukapita         INT NOT NULL,
            uemail          VARCHAR(255) NOT NULL UNIQUE,
            upassword       VARCHAR(255) NOT NULL,
            uphone          VARCHAR(50) NOT NULL,
            ubirth_date     DATE NOT NULL,
            uaddress        TEXT NOT NULL,
            unotes          TEXT,
            urole           VARCHAR(20) DEFAULT NULL,
            uregistered_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (ugereja) REFERENCES gereja(gkode),
            FOREIGN KEY (ukapita) REFERENCES kapita(idkapita)
        )
    """)

    # ── Tabel admin ──────────────────────────────────────────────────────────
    v_cursor.execute("""
        CREATE TABLE IF NOT EXISTS admin (
            aid             INT AUTO_INCREMENT PRIMARY KEY,
            ausername       VARCHAR(100) NOT NULL UNIQUE,
            aemail          VARCHAR(255) NOT NULL UNIQUE,
            apassword       VARCHAR(255) NOT NULL,
            arole           VARCHAR(20) DEFAULT NULL
        )
    """)

    # ── Tabel registrations ───────────────────────────────────────────────────
    v_cursor.execute("""
        CREATE TABLE IF NOT EXISTS registrations (
            id              INT AUTO_INCREMENT PRIMARY KEY,
            full_name       VARCHAR(255) NOT NULL,
            email           VARCHAR(255) NOT NULL UNIQUE,
            phone           VARCHAR(50) NOT NULL,
            birth_date      DATE NOT NULL,
            address         TEXT NOT NULL,
            church_gkode    VARCHAR(10) NOT NULL,
            kapita_id       INT NOT NULL,
            notes           TEXT,
            registered_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (church_gkode) REFERENCES gereja(gkode),
            FOREIGN KEY (kapita_id) REFERENCES kapita(idkapita)
        )
    """)

    v_conn.commit()
    v_conn.close()
    print("[DB] Database berhasil diinisialisasi.")


def seed_superadmin():
    from werkzeug.security import generate_password_hash
    from src import app

    v_conn = pymysql.connect(
        host=app.config["DB_HOST"],
        port=app.config["DB_PORT"],
        user=app.config["DB_USER"],
        password=app.config["DB_PASSWORD"],
        database=app.config["DB_NAME"],
        cursorclass=pymysql.cursors.DictCursor,
    )
    v_cursor = v_conn.cursor()

    v_cursor.execute("SELECT COUNT(*) AS cnt FROM admin")
    v_row = v_cursor.fetchone()

    if v_row["cnt"] == 0:
        v_hash = generate_password_hash("superadmin123")
        v_cursor.execute(
            "INSERT INTO admin (ausername, aemail, apassword, arole) VALUES (%s, %s, %s, %s)",
            ("superadmin", "superadmin@gereja.com", v_hash, "SuperAdmin")
        )
        v_conn.commit()
        print("[DB] SuperAdmin default dibuat: superadmin@gereja.com / superadmin123")

    v_conn.close()
