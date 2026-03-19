from app.database.db import get_db_connection
import mysql.connector 

def get_doctor_by_user(user_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT d.doctor_name, u.email, u.phone
        FROM Doctor d
        JOIN UserAccount u ON d.user_id = u.user_id
        WHERE d.user_id = %s
    """, (user_id,))

    doctor = cursor.fetchone()

    cursor.close()
    conn.close()

    return doctor

def update_doctor_profile(user_id, doctor_name, phone):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
        UPDATE Doctor
        SET doctor_name=%s
        WHERE user_id=%s
        """,(doctor_name,user_id))

        cursor.execute("""
        UPDATE UserAccount
        SET phone=%s
        WHERE user_id=%s
        """,(phone,user_id))

        conn.commit()
    
    except mysql.connector.IntegrityError:
        conn.rollback()
        raise ValueError("This Phone number already linked to another account")

    except Exception:
        conn.rollback()
        raise

    finally:
        cursor.close()
        conn.close()


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

