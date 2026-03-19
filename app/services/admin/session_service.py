from app.database.db import get_db_connection

def get_sessions_by_opd(opd_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            s.session_id,
            s.week_day,
            s.start_time,
            s.end_time,
            s.max_tokens_per_session,
            s.is_active,
            d.doctor_name
        FROM OPDSession s
        JOIN Doctor d ON s.doctor_id = d.doctor_id
        WHERE s.opd_id = %s
        ORDER BY FIELD(s.week_day, 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'), s.start_time
    """, (opd_id,))

    sessions = cursor.fetchall()

    cursor.close()
    conn.close()

    return sessions

def create_session(data):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        if data["is_email"]:
            email = data["email_or_phone"]
            phone = None
        else:
            phone = data["email_or_phone"]
            email = None

        # Doctor + OPD must belong to same department
        cursor.execute("""
            SELECT d.doctor_id
            FROM Doctor d
            JOIN UserAccount u
                ON d.user_id = u.user_id
            JOIN OPD o
                ON o.opd_id = %s
            WHERE (u.email = %s OR u.phone = %s)
              AND d.department_id = o.department_id
              AND d.is_active = TRUE
              AND o.is_active = TRUE
        """, (
            data["opd_id"],
            email,
            phone
        ))

        doctor = cursor.fetchone()

        if not doctor:
            raise ValueError("Doctor not found or does not belong to this department")

        doctor_id = doctor["doctor_id"]

        cursor.execute("""
            INSERT INTO OPDSession
            (doctor_id, opd_id, week_day, start_time, end_time, max_tokens_per_session)
            VALUES (%s,%s,%s,%s,%s,%s)
        """, (
            doctor_id,
            data["opd_id"],
            data["week_day"],
            data["start_time"],
            data["end_time"],
            data["max_tokens"]
        ))

        conn.commit()

    except Exception:
        conn.rollback()
        raise

    finally:
        cursor.close()
        conn.close()

def deactivate_session(session_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            UPDATE OPDSession
            SET is_active = FALSE
            WHERE session_id = %s
        """, (session_id,))

        conn.commit()

    except Exception:
        conn.rollback()
        raise

    finally:
        cursor.close()
        conn.close()

def activate_session(session_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # fetch session + doctor + opd
        cursor.execute("""
            SELECT 
                s.session_id,
                d.is_active AS doctor_active,
                o.is_active AS opd_active
            FROM OPDSession s
            JOIN Doctor d ON s.doctor_id = d.doctor_id
            JOIN OPD o ON s.opd_id = o.opd_id
            WHERE s.session_id = %s
        """, (session_id,))

        row = cursor.fetchone()
        if not row:
            raise ValueError("Session not found")
        if not row["doctor_active"]:
            raise ValueError("Cannot activate session. Doctor is not availale in this department")
        if not row["opd_active"]:
            raise ValueError("Cannot activate session. OPD is inactive")

        # safe to activate
        cursor.execute("""
            UPDATE OPDSession
            SET is_active = TRUE
            WHERE session_id = %s
        """, (session_id,))

        conn.commit()

    except Exception:
        conn.rollback()
        raise

    finally:
        cursor.close()
        conn.close()

def get_session_by_hospital_id(session_id, hospital_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT s.session_id
        FROM OPDSession s
        JOIN OPD o
            ON s.opd_id = o.opd_id
        WHERE s.session_id = %s
        AND o.hospital_id = %s
    """, (session_id, hospital_id))

    opd_session = cursor.fetchone()

    cursor.close()
    conn.close()

    return opd_session


