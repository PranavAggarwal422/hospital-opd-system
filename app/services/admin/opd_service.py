from app.database.db import get_db_connection
import mysql.connector


def get_opd_by_hospital_id(opd_id, hospital_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT opd_id, department_id, is_active
        FROM OPD
        WHERE opd_id = %s AND hospital_id = %s
    """, (opd_id, hospital_id))

    opd = cursor.fetchone()

    cursor.close()
    conn.close()

    return opd

def get_opd_by_department(department_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT opd_id, room_no, is_active
        FROM OPD
        WHERE department_id = %s
        ORDER BY is_active DESC, room_no
    """, (department_id,))

    opd_rooms = cursor.fetchall()

    cursor.close()
    conn.close()

    return opd_rooms

def create_opd(data):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO OPD
            (department_id, hospital_id, room_no)
            VALUES (%s,%s,%s)
        """, (
            data["department_id"],
            data["hospital_id"],
            data["room_no"]
        ))

        conn.commit()

    except mysql.connector.IntegrityError:
        conn.rollback()
        raise ValueError("Room already exists in hospital")

    except Exception:
        conn.rollback()
        raise

    finally:
        cursor.close()
        conn.close()

def deactivate_opd(opd_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # check active sessions
        cursor.execute("""
            SELECT COUNT(*) FROM OPDSession
            WHERE opd_id = %s AND is_active = TRUE
        """, (opd_id,))
        active_sessions = cursor.fetchone()[0]

        if active_sessions > 0:
            raise ValueError(f"Cannot deactivate OPD. {active_sessions} active session(s) exist.")

        cursor.execute("""
            UPDATE OPD
            SET is_active = FALSE
            WHERE opd_id = %s
        """, (opd_id,))

        conn.commit()

    except Exception:
        conn.rollback()
        raise

    finally:
        cursor.close()
        conn.close()
    
def activate_opd(opd_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT d.is_active AS dept_active
            FROM OPD o
            JOIN Department d ON o.department_id = d.department_id
            WHERE o.opd_id = %s
        """, (opd_id,))

        row = cursor.fetchone()
        if not row:
            raise ValueError("OPD not found")
        if not row["dept_active"]:
            raise ValueError("Cannot activate OPD. Department is inactive")

        cursor.execute("""
            UPDATE OPD
            SET is_active = TRUE
            WHERE opd_id = %s
        """, (opd_id,))

        conn.commit()

    except Exception:
        conn.rollback()
        raise

    finally:
        cursor.close()
        conn.close()

