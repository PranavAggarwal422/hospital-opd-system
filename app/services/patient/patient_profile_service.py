from app.database.db import get_db_connection
from datetime import datetime
import mysql.connector

def get_patient_by_id(patient_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            p.patient_id,
            p.patient_name,
            p.dob,
            p.gender,
            p.address,
            u.email,
            u.phone
        FROM Patient p
        JOIN UserAccount u
            ON p.user_id = u.user_id
        WHERE p.patient_id = %s
    """, (patient_id,))

    patient = cursor.fetchone()

    cursor.close()
    conn.close()

    return patient

def update_patient_profile(patient_id, data):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
        UPDATE Patient
        SET patient_name=%s,
            dob=%s,
            gender=%s,
            address = %s
        WHERE patient_id=%s
        """, (
            data["patient_name"],
            data["dob"],
            data["gender"],
            data["address"],
            patient_id
        ))

        cursor.execute("""
        UPDATE UserAccount
        SET email=%s,
            phone=%s
        WHERE user_id = (
            SELECT user_id
            FROM Patient
            WHERE patient_id=%s
        )
        """, (
            data["email"],
            data["phone"],
            patient_id
        ))

        conn.commit()

    except mysql.connector.IntegrityError:
        conn.rollback()
        raise ValueError("Email or Phone number already linked to another account")
    
    except Exception:
        conn.rollback()
        raise

    finally:
        cursor.close()
        conn.close()
