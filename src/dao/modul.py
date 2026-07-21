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
        v_new_id = v_cursor.fetchone()[0]
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
        v_result = v_cursor.fetchone()[0]
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
        v_result = v_cursor.fetchone()[0]
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
                COALESCE(r.reg_count, 0) + COALESCE(u.user_count, 0) AS registered,
                gk.kuota - COALESCE(r.reg_count, 0) - COALESCE(u.user_count, 0) AS quota_left
            FROM gereja_kapita gk
            JOIN kapita k ON k.idkapita = gk.idkapita
            LEFT JOIN (
                SELECT church_gkode, kapita_id, COUNT(*) AS reg_count
                FROM registrations
                GROUP BY church_gkode, kapita_id
            ) r ON r.church_gkode = gk.gkode AND r.kapita_id = gk.idkapita
            LEFT JOIN (
                SELECT ugereja, ukapita, COUNT(*) AS user_count
                FROM users
                GROUP BY ugereja, ukapita
            ) u ON u.ugereja = gk.gkode AND u.ukapita = gk.idkapita
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
                COALESCE(r.reg_count, 0) + COALESCE(u.user_count, 0) AS registered,
                gk.kuota - COALESCE(r.reg_count, 0) - COALESCE(u.user_count, 0) AS quota_left
            FROM gereja_kapita gk
            LEFT JOIN (
                SELECT church_gkode, kapita_id, COUNT(*) AS reg_count
                FROM registrations
                WHERE church_gkode = %s AND kapita_id = %s
            ) r ON r.church_gkode = gk.gkode AND r.kapita_id = gk.idkapita
            LEFT JOIN (
                SELECT ugereja, ukapita, COUNT(*) AS user_count
                FROM users
                WHERE ugereja = %s AND ukapita = %s
            ) u ON u.ugereja = gk.gkode AND u.ukapita = gk.idkapita
            WHERE gk.gkode = %s AND gk.idkapita = %s
        """, (p_gkode, p_idkapita, p_gkode, p_idkapita, p_gkode, p_idkapita))
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
        v_new_id = v_cursor.fetchone()[0]
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

def dao_create_registration(p_full_name, p_email, p_phone, p_birth_date, p_address, p_church_gkode, p_kapita_id, p_notes):
    v_cursor = None
    try:
        v_conn = get_connection()
        v_cursor = v_conn.cursor()
        v_cursor.execute("""
            INSERT INTO registrations (full_name, email, phone, birth_date, address, church_gkode, kapita_id, notes)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id
        """, (p_full_name, p_email, p_phone, p_birth_date, p_address, p_church_gkode, p_kapita_id, p_notes))
        v_new_id = v_cursor.fetchone()[0]
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
            SELECT r.id, r.full_name, r.email, r.phone, r.birth_date, r.address,
                   r.church_gkode, g.gkode, g.gnama AS church_name,
                   r.kapita_id, k.namakapita AS kapita_name,
                   r.notes, r.registered_at
            FROM registrations r
            JOIN gereja g ON g.gkode = r.church_gkode
            JOIN kapita k ON k.idkapita = r.kapita_id
            WHERE r.id = %s
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
            SELECT r.id, r.full_name, r.email, r.phone, r.birth_date, r.address,
                   r.church_gkode, g.gkode, g.gnama AS church_name,
                   r.kapita_id, k.namakapita AS kapita_name,
                   r.notes, r.registered_at
            FROM registrations r
            JOIN gereja g ON g.gkode = r.church_gkode
            JOIN kapita k ON k.idkapita = r.kapita_id
            WHERE r.email = %s
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
        v_cursor.execute(
            "SELECT COUNT(*) as count FROM registrations WHERE church_gkode = %s AND kapita_id = %s",
            (p_church_gkode, p_kapita_id)
        )
        v_row = v_cursor.fetchone()
        return v_row['count'] if v_row else 0
    except Exception as e:
        logger.error("dao_count_registrations_by_church_and_kapita: %s", str(e))
        raise
    finally:
        if v_cursor:
            v_cursor.close()


def dao_update_registration(p_id, p_full_name, p_email, p_phone, p_birth_date, p_address, p_church_gkode, p_kapita_id, p_notes):
    v_cursor = None
    try:
        v_conn = get_connection()
        v_cursor = v_conn.cursor()
        v_cursor.execute("""
            UPDATE registrations SET
                full_name = %s, email = %s, phone = %s, birth_date = %s,
                address = %s, church_gkode = %s, kapita_id = %s, notes = %s
            WHERE id = %s
        """, (p_full_name, p_email, p_phone, p_birth_date, p_address, p_church_gkode, p_kapita_id, p_notes, p_id))
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
        v_cursor.execute(
            'SELECT COUNT(*) as count FROM users WHERE ugereja = %s AND ukapita = %s',
            (p_church_gkode, p_kapita_id)
        )
        v_row = v_cursor.fetchone()
        return v_row['count'] if v_row else 0
    except Exception as e:
        logger.error("dao_count_users_by_church_and_kapita: %s", str(e))
        raise
    finally:
        if v_cursor:
            v_cursor.close()


def dao_create_user(p_full_name, p_email, p_phone, p_birth_date, p_address, p_church_gkode, p_ukapita, p_notes):
    v_cursor = None
    try:
        v_conn = get_connection()
        v_cursor = v_conn.cursor()
        v_cursor.execute("""
            INSERT INTO users (unama, uemail, uphone, ubirth_date, uaddress, ugereja, ukapita, unotes)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING uid
        """, (p_full_name, p_email, p_phone, p_birth_date, p_address, p_church_gkode, p_ukapita, p_notes))
        v_new_id = v_cursor.fetchone()[0]
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
            SELECT u.uid, u.unama, u.uemail, u.uphone, u.ubirth_date, u.uaddress,
                   u.ugereja, g.gkode, g.gnama AS church_name,
                   u.ukapita, k.namakapita AS kapita_name,
                   u.unotes, u.uregistered_at
            FROM users u
            JOIN gereja g ON g.gkode = u.ugereja
            JOIN kapita k ON k.idkapita = u.ukapita
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
            SELECT u.uid, u.unama, u.uemail, u.uphone, u.ubirth_date, u.uaddress,
                   u.ugereja, g.gkode, g.gnama AS church_name,
                   u.ukapita, k.namakapita AS kapita_name,
                   u.unotes, u.uregistered_at
            FROM users u
            JOIN gereja g ON g.gkode = u.ugereja
            JOIN kapita k ON k.idkapita = u.ukapita
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


def dao_update_user(p_uid, p_full_name, p_email, p_phone, p_birth_date, p_address, p_church_gkode, p_ukapita, p_notes):
    v_cursor = None
    try:
        v_conn = get_connection()
        v_cursor = v_conn.cursor()
        v_cursor.execute("""
            UPDATE users SET
                unama = %s, uemail = %s, uphone = %s, ubirth_date = %s,
                uaddress = %s, ugereja = %s, ukapita = %s, unotes = %s
            WHERE uid = %s
        """, (p_full_name, p_email, p_phone, p_birth_date, p_address, p_church_gkode, p_ukapita, p_notes, p_uid))
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
