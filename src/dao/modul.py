"""
dao/modul.py
Data Access Object untuk semua tabel (PostgreSQL via psycopg2).
"""
import logging
from src.database import get_connection
from src.utils import responseJson
from src.utils.db import execute, executeNoCommit, select

logger = logging.getLogger(__name__)


def _safe_fetch_value(p_cursor, p_key):
    v_row = p_cursor.fetchone()
    if v_row is None:
        return None
    if isinstance(v_row, dict):
        return v_row.get(p_key)
    if isinstance(v_row, (list, tuple)) and len(v_row) > 0:
        return v_row[0]
    return None


# ═══════════════════════════════════════════════════════════════════════════════
# PING DAO
# ═══════════════════════════════════════════════════════════════════════════════

def dao_ping():
    v_cursor = None
    try:
        v_conn = get_connection()
        v_cursor = v_conn.cursor()
        v_cursor.execute("SELECT EXISTS (SELECT 1 FROM users LIMIT 1)")
        v_result = v_cursor.fetchone()
        return v_result
    except Exception as e:
        logger.error("dao_ping: %s", str(e))
        raise
    finally:
        if v_cursor:
            v_cursor.close()


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
        v_new_id = _safe_fetch_value(v_cursor, "aid")
        if v_new_id is None:
            raise RuntimeError("Insert admin tidak mengembalikan aid.")
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
        v_result = _safe_fetch_value(v_cursor, "gkode")
        if v_result is None:
            raise RuntimeError("Insert gereja tidak mengembalikan gkode.")
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

def dao_set_church_kapita_quota(p_gkode, p_idkapita, p_kuota_sesi_1, p_kuota_sesi_2):
    v_cursor = None
    try:
        v_conn = get_connection()
        v_cursor = v_conn.cursor()
        v_cursor.execute("""
            INSERT INTO gereja_kapita (gkode, idkapita, kuota_sesi_1, kuota_sesi_2)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (gkode, idkapita) DO UPDATE SET
                kuota_sesi_1 = EXCLUDED.kuota_sesi_1,
                kuota_sesi_2 = EXCLUDED.kuota_sesi_2
            RETURNING gkid
        """, (p_gkode, p_idkapita, p_kuota_sesi_1, p_kuota_sesi_2))
        v_result = _safe_fetch_value(v_cursor, "gkid")
        if v_result is None:
            raise RuntimeError("Insert kuota gereja tidak mengembalikan gkid.")
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
            WITH participant_count AS (
                SELECT COUNT(*) AS total FROM participant WHERE pgereja = %s
            ),
            few_churches AS (
                SELECT COUNT(*) AS cnt FROM (
                    SELECT g.gkode
                    FROM gereja g
                    LEFT JOIN participant p ON p.pgereja = g.gkode
                    GROUP BY g.gkode
                    HAVING COUNT(p.pid) < 4
                ) t
            ),
            sesi_1 AS (
                SELECT ugereja AS gkode, ukapita_sesi_1 AS idkapita FROM users
                UNION ALL
                SELECT church_gkode AS gkode, kapita_id_sesi_1 AS idkapita FROM registrations
            ),
            sesi_2 AS (
                SELECT ugereja AS gkode, ukapita_sesi_2 AS idkapita FROM users
                UNION ALL
                SELECT church_gkode AS gkode, kapita_id_sesi_2 AS idkapita FROM registrations
            )
            SELECT
                gk.gkid            AS gkid,
                gk.gkode           AS gkode,
                gk.idkapita        AS idkapita,
                k.namakapita       AS kapita_name,
                gk.kuota_sesi_1    AS manual_kuota_sesi_1,
                gk.kuota_sesi_2    AS manual_kuota_sesi_2,
                COALESCE(r1.reg_count, 0) AS registered_sesi_1,
                COALESCE(r2.reg_count, 0) AS registered_sesi_2,
                CASE
                    WHEN gk.idkapita IN (5, 6)
                        THEN FLOOR(pc.total / 4) + CASE WHEN (pc.total %% 4) IN (1, 2, 3) THEN 1 ELSE 0 END
                    WHEN gk.idkapita IN (7, 8)
                        THEN FLOOR(pc.total / 4) + CASE WHEN (pc.total %% 4) = 3 THEN 1 ELSE 0 END
                    ELSE 0
                END + fc.cnt AS system_kuota
            FROM gereja_kapita gk
            JOIN kapita k ON k.idkapita = gk.idkapita
            CROSS JOIN participant_count pc
            CROSS JOIN few_churches fc
            LEFT JOIN (
                SELECT gkode, idkapita, COUNT(*) AS reg_count
                FROM sesi_1
                GROUP BY gkode, idkapita
            ) r1 ON r1.gkode = gk.gkode AND r1.idkapita = gk.idkapita
            LEFT JOIN (
                SELECT gkode, idkapita, COUNT(*) AS reg_count
                FROM sesi_2
                GROUP BY gkode, idkapita
            ) r2 ON r2.gkode = gk.gkode AND r2.idkapita = gk.idkapita
            WHERE gk.gkode = %s
            ORDER BY k.namakapita ASC
        """, (p_gkode, p_gkode))  # <-- Diubah menjadi (p_gkode, p_gkode)

        v_rows = []
        for v_row in v_cursor.fetchall() or []:
            if not v_row:
                continue
            v_manual_kuota_sesi_1 = v_row.get("manual_kuota_sesi_1", 0)
            v_manual_kuota_sesi_2 = v_row.get("manual_kuota_sesi_2", 0)
            v_system_kuota = v_row.get("system_kuota", 0)
            v_kuota_sesi_1 = max(v_manual_kuota_sesi_1, v_system_kuota)
            v_kuota_sesi_2 = max(v_manual_kuota_sesi_2, v_system_kuota)
            v_row["kuota_sesi_1"] = v_kuota_sesi_1
            v_row["kuota_sesi_2"] = v_kuota_sesi_2
            v_row["quota_left_sesi_1"] = v_kuota_sesi_1 - v_row.get("registered_sesi_1", 0)
            v_row["quota_left_sesi_2"] = v_kuota_sesi_2 - v_row.get("registered_sesi_2", 0)
            v_row.pop("manual_kuota_sesi_1", None)
            v_row.pop("manual_kuota_sesi_2", None)
            v_row.pop("system_kuota", None)
            v_rows.append(v_row)
        return v_rows
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
            WITH participant_count AS (
                SELECT COUNT(*) AS total FROM participant WHERE pgereja = %s
            ),
            few_churches AS (
                SELECT COUNT(*) AS cnt FROM (
                    SELECT g.gkode
                    FROM gereja g
                    LEFT JOIN participant p ON p.pgereja = g.gkode
                    GROUP BY g.gkode
                    HAVING COUNT(p.pid) < 4
                ) t
            ),
            sesi_1 AS (
                SELECT ugereja AS gkode, ukapita_sesi_1 AS idkapita FROM users
                UNION ALL
                SELECT church_gkode AS gkode, kapita_id_sesi_1 AS idkapita FROM registrations
            ),
            sesi_2 AS (
                SELECT ugereja AS gkode, ukapita_sesi_2 AS idkapita FROM users
                UNION ALL
                SELECT church_gkode AS gkode, kapita_id_sesi_2 AS idkapita FROM registrations
            )
            SELECT
                gk.gkid             AS gkid,
                gk.gkode            AS gkode,
                gk.idkapita         AS idkapita,
                gk.kuota_sesi_1     AS manual_kuota_sesi_1,
                gk.kuota_sesi_2     AS manual_kuota_sesi_2,
                COALESCE(r1.reg_count, 0) AS registered_sesi_1,
                COALESCE(r2.reg_count, 0) AS registered_sesi_2,
                CASE
                    WHEN gk.idkapita IN (5, 6)
                        THEN FLOOR(pc.total / 4) + CASE WHEN (pc.total %% 4) IN (1, 2, 3) THEN 1 ELSE 0 END
                    WHEN gk.idkapita IN (7, 8)
                        THEN FLOOR(pc.total / 4) + CASE WHEN (pc.total %% 4) = 3 THEN 1 ELSE 0 END
                    ELSE 0
                END + fc.cnt AS system_kuota
            FROM gereja_kapita gk
            CROSS JOIN participant_count pc
            CROSS JOIN few_churches fc
            LEFT JOIN (
                SELECT gkode, idkapita, COUNT(*) AS reg_count
                FROM sesi_1
                GROUP BY gkode, idkapita
            ) r1 ON r1.gkode = gk.gkode AND r1.idkapita = gk.idkapita
            LEFT JOIN (
                SELECT gkode, idkapita, COUNT(*) AS reg_count
                FROM sesi_2
                GROUP BY gkode, idkapita
            ) r2 ON r2.gkode = gk.gkode AND r2.idkapita = gk.idkapita
            WHERE gk.gkode = %s AND gk.idkapita = %s
        """, (p_gkode, p_gkode, p_idkapita))  # <-- Urutan parameter disesuaikan
        
        v_row = v_cursor.fetchone()
        if not v_row:
            return None
            
        v_kuota_sesi_1 = max(v_row["manual_kuota_sesi_1"], v_row["system_kuota"])
        v_kuota_sesi_2 = max(v_row["manual_kuota_sesi_2"], v_row["system_kuota"])
        v_row["kuota_sesi_1"] = v_kuota_sesi_1
        v_row["kuota_sesi_2"] = v_kuota_sesi_2
        v_row["quota_left_sesi_1"] = v_kuota_sesi_1 - v_row["registered_sesi_1"]
        v_row["quota_left_sesi_2"] = v_kuota_sesi_2 - v_row["registered_sesi_2"]
        v_row.pop("manual_kuota_sesi_1", None)
        v_row.pop("manual_kuota_sesi_2", None)
        v_row.pop("system_kuota", None)
        return dict(v_row)
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
# PARTICIPANT DAO
# ═══════════════════════════════════════════════════════════════════════════════

def dao_get_participant_by_id(p_pid):
    v_cursor = None
    try:
        v_conn = get_connection()
        v_cursor = v_conn.cursor()
        v_cursor.execute("SELECT pid, pnama, pgereja, pflag FROM participant WHERE pid = %s", (p_pid,))
        v_row = v_cursor.fetchone()
        return dict(v_row) if v_row else None
    except Exception as e:
        logger.error("dao_get_participant_by_id: %s", str(e))
        raise
    finally:
        if v_cursor:
            v_cursor.close()


def dao_get_participants_by_church(p_gereja):
    v_cursor = None
    try:
        v_conn = get_connection()
        v_cursor = v_conn.cursor()
        v_cursor.execute(
            "SELECT pid, pnama, pgereja, pflag FROM participant WHERE pgereja = %s ORDER BY pnama ASC",
            (p_gereja,)
        )
        return [dict(row) for row in v_cursor.fetchall()]
    except Exception as e:
        logger.error("dao_get_participants_by_church: %s", str(e))
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
        v_new_id = _safe_fetch_value(v_cursor, "idkapita")
        if v_new_id is None:
            raise RuntimeError("Insert kapita tidak mengembalikan idkapita.")
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

def dao_create_registration(p_unama, p_ugereja, p_kapita_id_sesi_1, p_kapita_id_sesi_2, p_uparticipant):
    v_cursor = None
    try:
        v_conn = get_connection()
        v_cursor = v_conn.cursor()
        v_cursor.execute("""
            INSERT INTO users (unama, ugereja, ukapita_sesi_1, ukapita_sesi_2, uparticipant)
            VALUES (%s, %s, %s, %s, %s) RETURNING uid
        """, (p_unama, p_ugereja, p_kapita_id_sesi_1, p_kapita_id_sesi_2, p_uparticipant))
        v_new_id = _safe_fetch_value(v_cursor, "uid")
        if v_new_id is None:
            raise RuntimeError("Insert registrasi tidak mengembalikan uid.")
        v_cursor.execute("UPDATE participant SET pflag = 'F' WHERE pid = %s", (p_uparticipant,))
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
            SELECT u.uid, u.unama AS full_name, u.ugereja AS church_gkode, g.gnama AS church_name,
                   u.ukapita_sesi_1 AS kapita_id_sesi_1, k1.namakapita AS kapita_name_sesi_1,
                   u.ukapita_sesi_2 AS kapita_id_sesi_2, k2.namakapita AS kapita_name_sesi_2,
                   u.uparticipant, u.uregistered_at AS registered_at
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


def dao_count_registrations_by_church_and_kapita(p_church_gkode, p_kapita_id):
    v_cursor = None
    try:
        v_conn = get_connection()
        v_cursor = v_conn.cursor()
        v_cursor.execute("""
            SELECT COUNT(*) as count FROM (
                SELECT ugereja AS gkode, ukapita_sesi_1 AS idkapita FROM users
                UNION ALL
                SELECT ugereja AS gkode, ukapita_sesi_2 AS idkapita FROM users
                UNION ALL
                SELECT church_gkode AS gkode, kapita_id_sesi_1 AS idkapita FROM registrations
                UNION ALL
                SELECT church_gkode AS gkode, kapita_id_sesi_2 AS idkapita FROM registrations
            ) expanded
            WHERE gkode = %s AND idkapita = %s
        """, (p_church_gkode, p_kapita_id))
        v_row = v_cursor.fetchone()
        return v_row['count'] if v_row else 0
    except Exception as e:
        logger.error("dao_count_registrations_by_church_and_kapita: %s", str(e))
        raise
    finally:
        if v_cursor:
            v_cursor.close()


def dao_update_registration(p_id, p_unama, p_ugereja, p_kapita_id_sesi_1, p_kapita_id_sesi_2, p_uparticipant):
    v_cursor = None
    try:
        v_conn = get_connection()
        v_cursor = v_conn.cursor()
        v_cursor.execute("SELECT uparticipant FROM users WHERE uid = %s", (p_id,))
        v_old_row = v_cursor.fetchone()
        v_old_participant = v_old_row["uparticipant"] if v_old_row else None
        v_cursor.execute("""
            UPDATE users SET
                unama = %s, ugereja = %s,
                ukapita_sesi_1 = %s, ukapita_sesi_2 = %s, uparticipant = %s
            WHERE uid = %s
        """, (p_unama, p_ugereja, p_kapita_id_sesi_1, p_kapita_id_sesi_2, p_uparticipant, p_id))
        if v_old_participant:
            v_cursor.execute("UPDATE participant SET pflag = 'T' WHERE pid = %s", (v_old_participant,))
        v_cursor.execute("UPDATE participant SET pflag = 'F' WHERE pid = %s", (p_uparticipant,))
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
        v_cursor.execute("SELECT uparticipant FROM users WHERE uid = %s", (p_id,))
        v_row = v_cursor.fetchone()
        if v_row and v_row["uparticipant"]:
            v_cursor.execute("UPDATE participant SET pflag = 'T' WHERE pid = %s", (v_row["uparticipant"],))
        v_cursor.execute("DELETE FROM users WHERE uid = %s", (p_id,))
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


def dao_create_user(p_unama, p_ugereja, p_ukapita_sesi_1, p_ukapita_sesi_2, p_uparticipant):
    try:
        v_conn = get_connection()

        v_insert = executeNoCommit(
            """
            INSERT INTO users (unama, ugereja, ukapita_sesi_1, ukapita_sesi_2, uparticipant)
            VALUES (%s, %s, %s, %s, %s) RETURNING uid
            """,
            (p_unama, p_ugereja, p_ukapita_sesi_1, p_ukapita_sesi_2, p_uparticipant),
            p_response="User insert berhasil.",
            p_return=True,
        )

        if v_insert["status"] == "F":
            return v_insert
        if not v_insert["results"]:
            return responseJson(500, "F", "Gagal mendapatkan id user setelah insert.", [])

        v_new_id = v_insert["results"][0]["uid"]

        v_update = executeNoCommit(
            "UPDATE participant SET pflag = 'F' WHERE pid = %s",
            (p_uparticipant,),
            p_response="Participant flag updated successfully.",
            p_return=False,
        )

        if v_update["status"] == "F":
            v_conn.rollback()
            return v_update

        v_conn.commit()
        return responseJson(200, "T", "User berhasil disimpan.", [{"uid": v_new_id}])
    except Exception as e:
        logger.error("dao_create_user: %s", str(e))
        raise


def dao_get_all_users():
    v_cursor = None
    try:
        v_conn = get_connection()
        v_cursor = v_conn.cursor()
        v_cursor.execute("""
            SELECT u.uid, u.unama, u.ugereja,
                   g.gkode, g.gnama AS church_name,
                   u.ukapita_sesi_1, k1.namakapita AS kapita_name_sesi_1,
                   u.ukapita_sesi_2, k2.namakapita AS kapita_name_sesi_2,
                   u.uparticipant, p.pnama AS participant_name,
                   u.uregistered_at
            FROM users u
            JOIN gereja g ON g.gkode = u.ugereja
            JOIN kapita k1 ON k1.idkapita = u.ukapita_sesi_1
            JOIN kapita k2 ON k2.idkapita = u.ukapita_sesi_2
            LEFT JOIN participant p ON p.pid = u.uparticipant
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
            SELECT u.uid, u.unama, u.ugereja,
                   g.gkode, g.gnama AS church_name,
                   u.ukapita_sesi_1, k1.namakapita AS kapita_name_sesi_1,
                   u.ukapita_sesi_2, k2.namakapita AS kapita_name_sesi_2,
                   u.uparticipant, p.pnama AS participant_name,
                   u.uregistered_at
            FROM users u
            JOIN gereja g ON g.gkode = u.ugereja
            JOIN kapita k1 ON k1.idkapita = u.ukapita_sesi_1
            JOIN kapita k2 ON k2.idkapita = u.ukapita_sesi_2
            LEFT JOIN participant p ON p.pid = u.uparticipant
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


def dao_update_user(p_uid, p_unama, p_ugereja, p_ukapita_sesi_1, p_ukapita_sesi_2, p_uparticipant):
    v_cursor = None
    try:
        v_conn = get_connection()
        v_cursor = v_conn.cursor()
        v_cursor.execute("SELECT uparticipant FROM users WHERE uid = %s", (p_uid,))
        v_old_row = v_cursor.fetchone()
        v_old_participant = v_old_row["uparticipant"] if v_old_row else None
        v_cursor.execute("""
            UPDATE users SET
                unama = %s, ugereja = %s,
                ukapita_sesi_1 = %s, ukapita_sesi_2 = %s, uparticipant = %s
            WHERE uid = %s
        """, (p_unama, p_ugereja, p_ukapita_sesi_1, p_ukapita_sesi_2, p_uparticipant, p_uid))
        if v_old_participant:
            v_cursor.execute("UPDATE participant SET pflag = 'T' WHERE pid = %s", (v_old_participant,))
        v_cursor.execute("UPDATE participant SET pflag = 'F' WHERE pid = %s", (p_uparticipant,))
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
        v_cursor.execute("SELECT uparticipant FROM users WHERE uid = %s", (p_uid,))
        v_row = v_cursor.fetchone()
        if v_row and v_row["uparticipant"]:
            v_cursor.execute("UPDATE participant SET pflag = 'T' WHERE pid = %s", (v_row["uparticipant"],))
        v_cursor.execute('DELETE FROM users WHERE uid = %s', (p_uid,))
        v_conn.commit()
        return v_cursor.rowcount > 0
    except Exception as e:
        logger.error("dao_delete_user: %s", str(e))
        raise
    finally:
        if v_cursor:
            v_cursor.close()


# ═══════════════════════════════════════════════════════════════════════════════
# CETAK EXCEL DAO
# ═══════════════════════════════════════════════════════════════════════════════

def dao_get_peserta_for_excel(p_pilihan, p_sesi_1=None, p_sesi_2=None, p_gkode=None):
    v_cursor = None
    try:
        v_conn = get_connection()
        v_cursor = v_conn.cursor()

        v_base_query = """
            SELECT * FROM (
                SELECT u.uid AS id, u.unama AS full_name,
                       u.ugereja AS church_gkode, g.gnama AS church_name,
                       u.ukapita_sesi_1 AS kapita_id_sesi_1, k1.namakapita AS kapita_name_sesi_1,
                       u.ukapita_sesi_2 AS kapita_id_sesi_2, k2.namakapita AS kapita_name_sesi_2,
                       u.uregistered_at AS registered_at
                FROM users u
                LEFT JOIN gereja g ON g.gkode = u.ugereja
                LEFT JOIN kapita k1 ON k1.idkapita = u.ukapita_sesi_1
                LEFT JOIN kapita k2 ON k2.idkapita = u.ukapita_sesi_2
            ) p
        """

        v_conditions = []
        v_params = []

        if p_gkode:
            v_conditions.append("p.church_gkode = %s")
            v_params.append(p_gkode)

        if p_sesi_1 is not None and str(p_sesi_1).strip() != "":
            v_conditions.append("p.kapita_id_sesi_1 = %s")
            v_params.append(int(p_sesi_1))

        if p_sesi_2 is not None and str(p_sesi_2).strip() != "":
            v_conditions.append("p.kapita_id_sesi_2 = %s")
            v_params.append(int(p_sesi_2))

        v_where_clause = ""
        if v_conditions:
            v_where_clause = " WHERE " + " AND ".join(v_conditions)

        if p_pilihan == 1:
            v_order_by = " ORDER BY p.id ASC"
        elif p_pilihan == 2:
            v_order_by = " ORDER BY p.church_name ASC, p.full_name ASC, p.id ASC"
        elif p_pilihan == 3:
            v_order_by = " ORDER BY p.kapita_name_sesi_1 ASC, p.kapita_name_sesi_2 ASC, p.full_name ASC, p.id ASC"
        elif p_pilihan == 4:
            v_order_by = " ORDER BY p.kapita_name_sesi_1 ASC, p.kapita_name_sesi_2 ASC, p.full_name ASC, p.id ASC"
        else:
            v_order_by = " ORDER BY p.id ASC"

        v_final_query = v_base_query + v_where_clause + v_order_by
        v_cursor.execute(v_final_query, tuple(v_params))
        return [dict(row) for row in v_cursor.fetchall()]
    except Exception as e:
        logger.error("dao_get_peserta_for_excel: %s", str(e))
        raise
    finally:
        if v_cursor:
            v_cursor.close()

