import psycopg2
from src.database import get_connection
from src.utils import responseJson


def _rows_to_list_of_dict(p_cursor):
    v_rows = p_cursor.fetchall()
    return [dict(v_row) for v_row in v_rows] if v_rows else []


def select(p_query, p_params=None, p_response="Data retrieved successfully."):
    v_cursor = None
    try:
        v_conn = get_connection()
        v_cursor = v_conn.cursor()
        v_cursor.execute(p_query, p_params or ())
        v_results = _rows_to_list_of_dict(v_cursor)
        return responseJson(200, "T", p_response, v_results)
    except psycopg2.Error as error:
        return responseJson(500, "F", f"Database error: {error}", [])
    finally:
        if v_cursor:
            v_cursor.close()


def execute(p_query, p_params=None, p_response="Operation completed successfully.", p_return=False):
    v_cursor = None
    try:
        v_conn = get_connection()
        v_cursor = v_conn.cursor()
        v_cursor.execute(p_query, p_params or ())
        v_results = _rows_to_list_of_dict(v_cursor) if p_return else []
        v_conn.commit()
        return responseJson(200, "T", p_response, v_results)
    except psycopg2.Error as error:
        return responseJson(500, "F", f"Database error: {error}", [])
    finally:
        if v_cursor:
            v_cursor.close()


def execute_no_commit(p_query, p_params=None, p_response="Operation completed successfully but changes are not yet committed.", p_return=False):
    v_cursor = None
    try:
        v_conn = get_connection()
        v_cursor = v_conn.cursor()
        v_cursor.execute(p_query, p_params or ())
        v_results = _rows_to_list_of_dict(v_cursor) if p_return else []
        return responseJson(200, "T", p_response, v_results)
    except psycopg2.Error as error:
        return responseJson(500, "F", f"Database error: {error}", [])
    finally:
        if v_cursor:
            v_cursor.close()


def executeNoCommit(p_query, p_params=None, p_response="Operation completed successfully but changes are not yet committed.", p_return=False):
    return execute_no_commit(p_query, p_params, p_response, p_return)
