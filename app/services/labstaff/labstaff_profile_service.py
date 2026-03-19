import mysql.connector
from app.database.db import get_db_connection

def get_lab_by_id(lab_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT lab_name, location
        FROM DiagnosticLab
        WHERE lab_id = %s
    """, (lab_id,))

    lab = cursor.fetchone()

    cursor.close()
    conn.close()

    return lab

def get_hospital_by_id(hospital_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
        SELECT *
        FROM Hospital
        WHERE hospital_id = %s
        """, (hospital_id,))

        hospital = cursor.fetchone()

        return hospital

    finally:
        cursor.close()
        conn.close()
        
def get_labstaff_by_user(user_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT ls.staff_name, ls.staff_role, u.email, u.phone
        FROM LabStaff ls
        JOIN UserAccount u
            ON ls.user_id = u.user_id
        WHERE ls.user_id = %s
    """, (user_id,))

    staff = cursor.fetchone()

    cursor.close()
    conn.close()

    return staff

def update_labstaff_profile(user_id, name, phone):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            UPDATE LabStaff
            SET staff_name = %s
            WHERE user_id = %s
        """, (name, user_id))

        cursor.execute("""
            UPDATE UserAccount
            SET phone = %s
            WHERE user_id = %s
        """, (phone, user_id))

        conn.commit()

    except mysql.connector.IntegrityError:
        conn.rollback()
        raise ValueError("Phone already linked to another account")

    except Exception:
        conn.rollback()
        raise

    finally:
        cursor.close()
        conn.close()

