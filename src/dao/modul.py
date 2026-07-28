"""
dao/modul.py
Data Access Object untuk semua tabel (PostgreSQL via psycopg2).
"""
import logging
from src.database import get_connection

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════════
# ADMIN DAO
# ═══════════════════════════════════════════════════════════════════════════════

def dao_create_admin(p_username, p_email, p_password_hash, p_role):
    v_cursor = None
    try:
        v_conn = get_connection()
        v_cursor = v_conn.cursor()
        v_role = None if p_role == "NULL" else p_role
        v_cursor.execute(
            "INSERT INTO admin (ausername, aemail, apassword, arole) VALUES (%s, %s, %s, %s) RETURNING aid",
            (p_username, p_email, p_password_hash, v_role)
        )
        v_new_id = v_cursor.fetchone()["aid"]
        v_conn.commit()
        return v_new_id
    except Exception as e:
        logger.error("dao_create_admin: %s", str(e))
        raise
    finally:
        if v_cursor:
            v_cursor.close()


def dao_get_all_admins():
    v_cursor = None
    try:
        v_conn = get_connection()
        v_cursor = v_conn.cursor()
        v_cursor.execute("SELECT aid, ausername, aemail, arole FROM admin ORDER BY ausername ASC")
        return [dict(row) for row in v_cursor.fetchall()]
    except Exception as e:
        logger.error("dao_get_all_admins: %s", str(e))
        raise
    finally:
        if v_cursor:
            v_cursor.close()


def dao_get_admin_by_id(p_aid):
    v_cursor = None
    try:
        v_conn = get_connection()
        v_cursor = v_conn.cursor()
        v_cursor.execute("SELECT aid, ausername, aemail, arole FROM admin WHERE aid = %s", (p_aid,))
        v_row = v_cursor.fetchone()
        return dict(v_row) if v_row else None
    except Exception as e:
        logger.error("dao_get_admin_by_id: %s", str(e))
        raise
    finally:
        if v_cursor:
            v_cursor.close()


def dao_get_admin_by_email(p_email):
    v_cursor = None
    try:
        v_conn = get_connection()
        v_cursor = v_conn.cursor()
        v_cursor.execute("SELECT aid, ausername, aemail, apassword, arole FROM admin WHERE aemail = %s", (p_email,))
        v_row = v_cursor.fetchone()
        return dict(v_row) if v_row else None
    except Exception as e:
        logger.error("dao_get_admin_by_email: %s", str(e))
        raise
    finally:
        if v_cursor:
            v_cursor.close()


def dao_get_admin_with_password_by_id(p_aid):
    v_cursor = None
    try:
        v_conn = get_connection()
        v_cursor = v_conn.cursor()
        v_cursor.execute("SELECT aid, ausername, aemail, apassword, arole FROM admin WHERE aid = %s", (p_aid,))
        v_row = v_cursor.fetchone()
        return dict(v_row) if v_row else None
    except Exception as e:
        logger.error("dao_get_admin_with_password_by_id: %s", str(e))
        raise
    finally:
        if v_cursor:
            v_cursor.close()


def dao_update_admin(p_aid, p_username, p_email, p_password_hash, p_role):
    v_cursor = None
    try:
        v_conn = get_connection()
        v_cursor = v_conn.cursor()
        v_fields, v_values = [], []
        if p_username is not None:
            v_fields.append("ausername = %s"); v_values.append(p_username)
        if p_email is not None:
            v_fields.append("aemail = %s"); v_values.append(p_email)
        if p_password_hash is not None:
            v_fields.append("apassword = %s"); v_values.append(p_password_hash)
        if p_role is not None:
            v_fields.append("arole = %s"); v_values.append(None if p_role == "NULL" else p_role)
        if not v_fields:
            return False
        v_values.append(p_aid)
        v_cursor.execute(f"UPDATE admin SET {', '.join(v_fields)} WHERE aid = %s", tuple(v_values))
        v_conn.commit()
        return v_cursor.rowcount > 0
    except Exception as e:
        logger.error("dao_update_admin: %s", str(e))
        raise
    finally:
        if v_cursor:
            v_cursor.close()


def dao_delete_admin(p_aid):
    v_cursor = None
    try:
        v_conn = get_connection()
        v_cursor = v_conn.cursor()
        v_cursor.execute("DELETE FROM admin WHERE aid = %s", (p_aid,))
        v_conn.commit()
        return v_cursor.rowcount > 0
    except Exception as e:
        logger.error("dao_delete_admin: %s", str(e))
        raise
    finally:
        if v_cursor:
            v_cursor.close()


# ═══════════════════════════════════════════════════════════════════════════════
# GEREJA DAO
# ═══════════════════════════════════════════════════════════════════════════════

def _generate_gkode(p_gnama, p_cursor):
    v_prefix = p_gnama.strip().split()[0].upper()
    p_cursor.execute(
        "SELECT COUNT(*) AS cnt FROM gereja WHERE gkode LIKE %s",
        (f"{v_prefix}%",)
    )
    v_row = p_cursor.fetchone()
    v_count = v_row['cnt'] if v_row else 0
    return f"{v_prefix}{v_count + 1:03d}"


def dao_get_all_churches():
    v_cursor = None
    try:
        v_conn = get_connection()
        v_cursor = v_conn.cursor()
        v_cursor.execute("SELECT gkode, gnama AS name FROM gereja ORDER BY gnama ASC")
        return [dict(row) for row in v_cursor.fetchall()]
    except Exception as e:
        logger.error("dao_get_all_churches: %s", str(e))
        raise
    finally:
        if v_cursor:
            v_cursor.close()


def dao_get_church_by_gkode(p_gkode):
    v_cursor = None
    try:
        v_conn = get_connection()
        v_cursor = v_conn.cursor()
        v_cursor.execute("SELECT gkode, gnama AS name FROM gereja WHERE gkode = %s", (p_gkode,))
        v_row = v_cursor.fetchone()
        return dict(v_row) if v_row else None
    except Exception as e:
        logger.error("dao_get_church_by_gkode: %s", str(e))
        raise
    finally:
        if v_cursor:
            v_cursor.close()


def dao_create_church(p_gnama):
    v_cursor = None
    try:
        v_conn = get_connection()
        v_cursor = v_conn.cursor()
        v_gkode = _generate_gkode(p_gnama, v_cursor)
        v_cursor.execute("INSERT INTO gereja (gkode, gnama) VALUES (%s, %s) RETURNING gkode", (v_gkode, p_gnama))
        v_result = v_cursor.fetchone()["gkode"]
        v_conn.commit()
        return v_result
    except Exception as e:
        logger.error("dao_create_church: %s", str(e))
        raise
    finally:
        if v_cursor:
            v_cursor.close()


def dao_update_church(p_gkode, p_gnama):
    v_cursor = None
    try:
        v_conn = get_connection()
        v_cursor = v_conn.cursor()
        v_cursor.execute("UPDATE gereja SET gnama = %s WHERE gkode = %s", (p_gnama, p_gkode))
        v_conn.commit()
        return v_cursor.rowcount > 0
    except Exception as e:
        logger.error("dao_update_church: %s", str(e))
        raise
    finally:
        if v_cursor:
            v_cursor.close()


def dao_delete_church(p_gkode):
    v_cursor = None
    try:
        v_conn = get_connection()
        v_cursor = v_conn.cursor()
        v_cursor.execute("DELETE FROM gereja WHERE gkode = %s", (p_gkode,))
        v_conn.commit()
        return v_cursor.rowcount > 0
    except Exception as e:
        logger.error("dao_delete_church: %s", str(e))
        raise
    finally:
        if v_cursor:
            v_cursor.close()


# ═══════════════════════════════════════════════════════════════════════════════
# GEREJA_KAPITA DAO (kuota per gereja per KAPITA)
# ═══════════════════════════════════════════════════════════════════════════════

def dao_set_church_kapita_quota(p_gkode, p_idkapita, p_kuota):
    v_cursor = None
    try:
        v_conn = get_connection()
        v_cursor = v_conn.cursor()
        v_cursor.execute("""
            INSERT INTO gereja_kapita (gkode, idkapita, kuota)
            VALUES (%s, %s, %s)
            ON CONFLICT (gkode, idkapita) DO UPDATE SET kuota = EXCLUDED.kuota
            RETURNING gkid
        """, (p_gkode, p_idkapita, p_kuota))
        v_result = v_cursor.fetchone()["gkid"]
        v_conn.commit()
        return v_result
    except Exception as e:
        logger.error("dao_set_church_kapita_quota: %s", str(e))
        raise
    finally:
        if v_cursor:
            v_cursor.close()


def dao_get_church_kapita_quotas(p_gkode):
    v_cursor = None
    try:
        v_conn = get_connection()
        v_cursor = v_conn.cursor()
        v_cursor.execute("""
            SELECT
                gk.gkid        AS gkid,
                gk.gkode       AS gkode,
                gk.idkapita    AS idkapita,
                k.namakapita   AS kapita_name,
                gk.kuota       AS kuota,
                COALESCE(r.reg_count, 0) AS registered,
                gk.kuota - COALESCE(r.reg_count, 0) AS quota_left
            FROM gereja_kapita gk
            JOIN kapita k ON k.idkapita = gk.idkapita
            LEFT JOIN (
                SELECT gkode, idkapita, COUNT(*) AS reg_count
                FROM (
                    SELECT church_gkode AS gkode, kapita_id_sesi_1 AS idkapita FROM registrations
                    UNION ALL
                    SELECT church_gkode AS gkode, kapita_id_sesi_2 AS idkapita FROM registrations
                ) expanded
                GROUP BY gkode, idkapita
            ) r ON r.gkode = gk.gkode AND r.idkapita = gk.idkapita
            WHERE gk.gkode = %s
            ORDER BY k.namakapita ASC
        """, (p_gkode,))
        return [dict(row) for row in v_cursor.fetchall()]
    except Exception as e:
        logger.error("dao_get_church_kapita_quotas: %s", str(e))
        raise
    finally:
        if v_cursor:
            v_cursor.close()


def dao_count_all_registrations_by_church(p_gkode):
    v_cursor = None
    try:
        v_conn = get_connection()
        v_cursor = v_conn.cursor()
        v_cursor.execute("SELECT COUNT(*) AS count FROM registrations WHERE church_gkode = %s", (p_gkode,))
        v_row = v_cursor.fetchone()
        return v_row['count'] if v_row else 0
    except Exception as e:
        logger.error("dao_count_all_registrations_by_church: %s", str(e))
        raise
    finally:
        if v_cursor:
            v_cursor.close()


def dao_count_all_users_by_church(p_gkode):
    v_cursor = None
    try:
        v_conn = get_connection()
        v_cursor = v_conn.cursor()
        v_cursor.execute('SELECT COUNT(*) AS count FROM users WHERE ugereja = %s', (p_gkode,))
        v_row = v_cursor.fetchone()
        return v_row['count'] if v_row else 0
    except Exception as e:
        logger.error("dao_count_all_users_by_church: %s", str(e))
        raise
    finally:
        if v_cursor:
            v_cursor.close()


def dao_get_quota_by_church_and_kapita(p_gkode, p_idkapita):
    v_cursor = None
    try:
        v_conn = get_connection()
        v_cursor = v_conn.cursor()
        v_cursor.execute("""
            SELECT
                gk.gkid        AS gkid,
                gk.gkode       AS gkode,
                gk.idkapita    AS idkapita,
                gk.kuota       AS kuota,
                COALESCE(r.reg_count, 0) AS registered,
                gk.kuota - COALESCE(r.reg_count, 0) AS quota_left
            FROM gereja_kapita gk
            LEFT JOIN (
                SELECT gkode, idkapita, COUNT(*) AS reg_count
                FROM (
                    SELECT church_gkode AS gkode, kapita_id_sesi_1 AS idkapita FROM registrations
                    UNION ALL
                    SELECT church_gkode AS gkode, kapita_id_sesi_2 AS idkapita FROM registrations
                ) expanded
                WHERE gkode = %s AND idkapita = %s
                GROUP BY gkode, idkapita
            ) r ON r.gkode = gk.gkode AND r.idkapita = gk.idkapita
            WHERE gk.gkode = %s AND gk.idkapita = %s
        """, (p_gkode, p_idkapita, p_gkode, p_idkapita))
        v_row = v_cursor.fetchone()
        return dict(v_row) if v_row else None
    except Exception as e:
        logger.error("dao_get_quota_by_church_and_kapita: %s", str(e))
        raise
    finally:
        if v_cursor:
            v_cursor.close()


def dao_delete_church_kapita_quota(p_gkode, p_idkapita):
    v_cursor = None
    try:
        v_conn = get_connection()
        v_cursor = v_conn.cursor()
        v_cursor.execute("DELETE FROM gereja_kapita WHERE gkode = %s AND idkapita = %s", (p_gkode, p_idkapita))
        v_conn.commit()
        return v_cursor.rowcount > 0
    except Exception as e:
        logger.error("dao_delete_church_kapita_quota: %s", str(e))
        raise
    finally:
        if v_cursor:
            v_cursor.close()


# ═══════════════════════════════════════════════════════════════════════════════
# KAPITA DAO
# ═══════════════════════════════════════════════════════════════════════════════

def dao_create_kapita(p_namakapita):
    v_cursor = None
    try:
        v_conn = get_connection()
        v_cursor = v_conn.cursor()
        v_cursor.execute("INSERT INTO kapita (namakapita) VALUES (%s) RETURNING idkapita", (p_namakapita,))
        v_new_id = v_cursor.fetchone()["idkapita"]
        v_conn.commit()
        return v_new_id
    except Exception as e:
        logger.error("dao_create_kapita: %s", str(e))
        raise
    finally:
        if v_cursor:
            v_cursor.close()


def dao_get_all_kapita():
    v_cursor = None
    try:
        v_conn = get_connection()
        v_cursor = v_conn.cursor()
        v_cursor.execute("SELECT idkapita, namakapita FROM kapita ORDER BY namakapita ASC")
        return [dict(row) for row in v_cursor.fetchall()]
    except Exception as e:
        logger.error("dao_get_all_kapita: %s", str(e))
        raise
    finally:
        if v_cursor:
            v_cursor.close()


def dao_get_kapita_by_id(p_idkapita):
    v_cursor = None
    try:
        v_conn = get_connection()
        v_cursor = v_conn.cursor()
        v_cursor.execute("SELECT idkapita, namakapita FROM kapita WHERE idkapita = %s", (p_idkapita,))
        v_row = v_cursor.fetchone()
        return dict(v_row) if v_row else None
    except Exception as e:
        logger.error("dao_get_kapita_by_id: %s", str(e))
        raise
    finally:
        if v_cursor:
            v_cursor.close()


def dao_update_kapita(p_idkapita, p_namakapita):
    v_cursor = None
    try:
        v_conn = get_connection()
        v_cursor = v_conn.cursor()
        v_cursor.execute("UPDATE kapita SET namakapita = %s WHERE idkapita = %s", (p_namakapita, p_idkapita))
        v_conn.commit()
        return v_cursor.rowcount > 0
    except Exception as e:
        logger.error("dao_update_kapita: %s", str(e))
        raise
    finally:
        if v_cursor:
            v_cursor.close()


def dao_delete_kapita(p_idkapita):
    v_cursor = None
    try:
        v_conn = get_connection()
        v_cursor = v_conn.cursor()
        v_cursor.execute("DELETE FROM kapita WHERE idkapita = %s", (p_idkapita,))
        v_conn.commit()
        return v_cursor.rowcount > 0
    except Exception as e:
        logger.error("dao_delete_kapita: %s", str(e))
        raise
    finally:
        if v_cursor:
            v_cursor.close()


# ═══════════════════════════════════════════════════════════════════════════════
# REGISTRATIONS DAO
# ═══════════════════════════════════════════════════════════════════════════════

def dao_create_registration(p_full_name, p_email, p_phone, p_church_gkode, p_kapita_id_sesi_1, p_kapita_id_sesi_2):
    v_cursor = None
    try:
        v_conn = get_connection()
        v_cursor = v_conn.cursor()
        v_cursor.execute("""
            INSERT INTO users (unama, uemail, uphone, ugereja, ukapita_sesi_1, ukapita_sesi_2)
            VALUES (%s, %s, %s, %s, %s, %s) RETURNING uid
        """, (p_full_name, p_email, p_phone, p_church_gkode, p_kapita_id_sesi_1, p_kapita_id_sesi_2))
        v_new_id = v_cursor.fetchone()["uid"]
        v_conn.commit()
        return v_new_id
    except Exception as e:
        logger.error("dao_create_registration: %s", str(e))
        raise
    finally:
        if v_cursor:
            v_cursor.close()


def dao_get_registration_by_id(p_reg_id):
    v_cursor = None
    try:
        v_conn = get_connection()
        v_cursor = v_conn.cursor()
        v_cursor.execute("""
            SELECT u.uid, u.unama AS full_name, u.uemail AS email, u.uphone AS phone,
                   u.ugereja AS church_gkode, g.gkode, g.gnama AS church_name,
                   u.ukapita_sesi_1 AS kapita_id_sesi_1, k1.namakapita AS kapita_name_sesi_1,
                   u.ukapita_sesi_2 AS kapita_id_sesi_2, k2.namakapita AS kapita_name_sesi_2,
                   u.uregistered_at AS registered_at
            FROM users u
            LEFT JOIN gereja g ON g.gkode = u.ugereja
            LEFT JOIN kapita k1 ON k1.idkapita = u.ukapita_sesi_1
            LEFT JOIN kapita k2 ON k2.idkapita = u.ukapita_sesi_2
            WHERE u.uid = %s
        """, (p_reg_id,))
        v_row = v_cursor.fetchone()
        return dict(v_row) if v_row else None
    except Exception as e:
        logger.error("dao_get_registration_by_id: %s", str(e))
        raise
    finally:
        if v_cursor:
            v_cursor.close()


def dao_get_registration_by_email(p_email):
    v_cursor = None
    try:
        v_conn = get_connection()
        v_cursor = v_conn.cursor()
        v_cursor.execute("""
            SELECT u.uid, u.unama AS full_name, u.uemail AS email, u.uphone AS phone,
                   u.ugereja AS church_gkode, g.gkode, g.gnama AS church_name,
                   u.ukapita_sesi_1 AS kapita_id_sesi_1, k1.namakapita AS kapita_name_sesi_1,
                   u.ukapita_sesi_2 AS kapita_id_sesi_2, k2.namakapita AS kapita_name_sesi_2,
                   u.uregistered_at AS registered_at
            FROM users u
            LEFT JOIN gereja g ON g.gkode = u.ugereja
            LEFT JOIN kapita k1 ON k1.idkapita = u.ukapita_sesi_1
            LEFT JOIN kapita k2 ON k2.idkapita = u.ukapita_sesi_2
            WHERE u.uemail = %s
        """, (p_email,))
        v_row = v_cursor.fetchone()
        return dict(v_row) if v_row else None
    except Exception as e:
        logger.error("dao_get_registration_by_email: %s", str(e))
        raise
    finally:
        if v_cursor:
            v_cursor.close()


def dao_count_registrations_by_church_and_kapita(p_church_gkode, p_kapita_id):
    v_cursor = None
    try:
        v_conn = get_connection()
        v_cursor = v_conn.cursor()
        v_cursor.execute("""
            SELECT COUNT(*) as count FROM registrations
            WHERE church_gkode = %s AND (kapita_id_sesi_1 = %s OR kapita_id_sesi_2 = %s)
        """, (p_church_gkode, p_kapita_id, p_kapita_id))
        v_row = v_cursor.fetchone()
        return v_row['count'] if v_row else 0
    except Exception as e:
        logger.error("dao_count_registrations_by_church_and_kapita: %s", str(e))
        raise
    finally:
        if v_cursor:
            v_cursor.close()


def dao_update_registration(p_id, p_full_name, p_email, p_phone, p_church_gkode, p_kapita_id_sesi_1, p_kapita_id_sesi_2):
    v_cursor = None
    try:
        v_conn = get_connection()
        v_cursor = v_conn.cursor()
        v_cursor.execute("""
            UPDATE registrations SET
                full_name = %s, email = %s, phone = %s,
                church_gkode = %s, kapita_id_sesi_1 = %s, kapita_id_sesi_2 = %s
            WHERE id = %s
        """, (p_full_name, p_email, p_phone, p_church_gkode, p_kapita_id_sesi_1, p_kapita_id_sesi_2, p_id))
        v_conn.commit()
        return v_cursor.rowcount > 0
    except Exception as e:
        logger.error("dao_update_registration: %s", str(e))
        raise
    finally:
        if v_cursor:
            v_cursor.close()


def dao_delete_registration(p_id):
    v_cursor = None
    try:
        v_conn = get_connection()
        v_cursor = v_conn.cursor()
        v_cursor.execute("DELETE FROM registrations WHERE id = %s", (p_id,))
        v_conn.commit()
        return v_cursor.rowcount > 0
    except Exception as e:
        logger.error("dao_delete_registration: %s", str(e))
        raise
    finally:
        if v_cursor:
            v_cursor.close()


# ═══════════════════════════════════════════════════════════════════════════════
# USER DAO
# ═══════════════════════════════════════════════════════════════════════════════

def dao_count_users_by_church_and_kapita(p_church_gkode, p_kapita_id):
    v_cursor = None
    try:
        v_conn = get_connection()
        v_cursor = v_conn.cursor()
        v_cursor.execute("""
            SELECT COUNT(*) as count FROM users
            WHERE ugereja = %s AND (ukapita_sesi_1 = %s OR ukapita_sesi_2 = %s)
        """, (p_church_gkode, p_kapita_id, p_kapita_id))
        v_row = v_cursor.fetchone()
        return v_row['count'] if v_row else 0
    except Exception as e:
        logger.error("dao_count_users_by_church_and_kapita: %s", str(e))
        raise
    finally:
        if v_cursor:
            v_cursor.close()


def dao_create_user(p_full_name, p_email, p_phone, p_church_gkode, p_ukapita_sesi_1, p_ukapita_sesi_2):
    v_cursor = None
    try:
        v_conn = get_connection()
        v_cursor = v_conn.cursor()
        v_cursor.execute("""
            INSERT INTO users (unama, uemail, uphone, ugereja, ukapita_sesi_1, ukapita_sesi_2)
            VALUES (%s, %s, %s, %s, %s, %s) RETURNING uid
        """, (p_full_name, p_email, p_phone, p_church_gkode, p_ukapita_sesi_1, p_ukapita_sesi_2))
        v_new_id = v_cursor.fetchone()["uid"]
        v_conn.commit()
        return v_new_id
    except Exception as e:
        logger.error("dao_create_user: %s", str(e))
        raise
    finally:
        if v_cursor:
            v_cursor.close()


def dao_get_all_users():
    v_cursor = None
    try:
        v_conn = get_connection()
        v_cursor = v_conn.cursor()
        v_cursor.execute("""
            SELECT u.uid, u.unama, u.uemail, u.uphone,
                   u.ugereja, g.gkode, g.gnama AS church_name,
                   u.ukapita_sesi_1, k1.namakapita AS kapita_name_sesi_1,
                   u.ukapita_sesi_2, k2.namakapita AS kapita_name_sesi_2,
                   u.uregistered_at
            FROM users u
            JOIN gereja g ON g.gkode = u.ugereja
            JOIN kapita k1 ON k1.idkapita = u.ukapita_sesi_1
            JOIN kapita k2 ON k2.idkapita = u.ukapita_sesi_2
            ORDER BY u.unama ASC
        """)
        return [dict(row) for row in v_cursor.fetchall()]
    except Exception as e:
        logger.error("dao_get_all_users: %s", str(e))
        raise
    finally:
        if v_cursor:
            v_cursor.close()


def dao_get_user_by_id(p_uid):
    v_cursor = None
    try:
        v_conn = get_connection()
        v_cursor = v_conn.cursor()
        v_cursor.execute("""
            SELECT u.uid, u.unama, u.uemail, u.uphone,
                   u.ugereja, g.gkode, g.gnama AS church_name,
                   u.ukapita_sesi_1, k1.namakapita AS kapita_name_sesi_1,
                   u.ukapita_sesi_2, k2.namakapita AS kapita_name_sesi_2,
                   u.uregistered_at
            FROM users u
            JOIN gereja g ON g.gkode = u.ugereja
            JOIN kapita k1 ON k1.idkapita = u.ukapita_sesi_1
            JOIN kapita k2 ON k2.idkapita = u.ukapita_sesi_2
            WHERE u.uid = %s
        """, (p_uid,))
        v_row = v_cursor.fetchone()
        return dict(v_row) if v_row else None
    except Exception as e:
        logger.error("dao_get_user_by_id: %s", str(e))
        raise
    finally:
        if v_cursor:
            v_cursor.close()


def dao_update_user(p_uid, p_full_name, p_email, p_phone, p_church_gkode, p_ukapita_sesi_1, p_ukapita_sesi_2):
    v_cursor = None
    try:
        v_conn = get_connection()
        v_cursor = v_conn.cursor()
        v_cursor.execute("""
            UPDATE users SET
                unama = %s, uemail = %s, uphone = %s,
                ugereja = %s, ukapita_sesi_1 = %s, ukapita_sesi_2 = %s
            WHERE uid = %s
        """, (p_full_name, p_email, p_phone, p_church_gkode, p_ukapita_sesi_1, p_ukapita_sesi_2, p_uid))
        v_conn.commit()
        return v_cursor.rowcount > 0
    except Exception as e:
        logger.error("dao_update_user: %s", str(e))
        raise
    finally:
        if v_cursor:
            v_cursor.close()


def dao_delete_user(p_uid):
    v_cursor = None
    try:
        v_conn = get_connection()
        v_cursor = v_conn.cursor()
        v_cursor.execute('DELETE FROM users WHERE uid = %s', (p_uid,))
        v_conn.commit()
        return v_cursor.rowcount > 0
    except Exception as e:
        logger.error("dao_delete_user: %s", str(e))
        raise
    finally:
        if v_cursor:
            v_cursor.close()
