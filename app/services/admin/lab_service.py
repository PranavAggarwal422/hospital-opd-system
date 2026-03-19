from app.database.db import get_db_connection
import mysql.connector


def get_labs_by_hospital(hospital_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT lab_id, lab_name, location, is_active
        FROM DiagnosticLab
        WHERE hospital_id = %s
        ORDER BY is_active DESC, lab_name
    """, (hospital_id,))

    labs = cursor.fetchall()

    cursor.close()
    conn.close()

    return labs

def get_lab_by_hospital(lab_id, hospital_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT lab_id, lab_name, location, is_active
        FROM DiagnosticLab
        WHERE lab_id = %s
        AND hospital_id = %s
    """, (lab_id, hospital_id))

    lab = cursor.fetchone()

    cursor.close()
    conn.close()

    return lab

def create_lab(data):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO DiagnosticLab
            (hospital_id, lab_name, location)
            VALUES (%s,%s,%s)
        """, (
            data["hospital_id"],
            data["lab_name"],
            data["location"]
        ))

        conn.commit()

    except mysql.connector.IntegrityError:
        conn.rollback()
        raise ValueError("Lab already exists in this hospital")

    except Exception:
        conn.rollback()
        raise

    finally:
        cursor.close()
        conn.close()

def set_lab_status(lab_id, status):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        if status == False:
            # check active staff
            cursor.execute("""
                SELECT COUNT(*) FROM LabStaff
                WHERE lab_id = %s AND is_active = TRUE
            """, (lab_id,))
            active_staff = cursor.fetchone()[0]

            if active_staff > 0:
                raise ValueError(f"Cannot deactivate lab. {active_staff} active staff member(s) exist.")

            # check pending test requests
            cursor.execute("""
                SELECT COUNT(*) FROM TestRequest
                WHERE lab_id = %s
                AND test_status != 'Completed'
            """, (lab_id,))
            pending_tests = cursor.fetchone()[0]

            if pending_tests > 0:
                raise ValueError(f"Cannot deactivate lab. {pending_tests} pending test request(s) exist.")

        # update lab status
        cursor.execute("""
            UPDATE DiagnosticLab
            SET is_active = %s
            WHERE lab_id = %s
        """, (status, lab_id))

        # if lab is being deactivated → disable tests
        if not status:
            cursor.execute("""
                UPDATE LabSupportTest
                SET is_available = FALSE
                WHERE lab_id = %s
            """, (lab_id,))

        conn.commit()

    except Exception:
        conn.rollback()
        raise

    finally:
        cursor.close()
        conn.close()


