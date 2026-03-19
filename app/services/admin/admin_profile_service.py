from app.database.db import get_db_connection
import mysql.connector

def get_admin_by_user(user_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
    SELECT a.admin_name, u.email, u.phone
    FROM Admin a
    JOIN UserAccount u ON a.user_id = u.user_id
    WHERE a.user_id=%s
    """,(user_id,))

    admin = cursor.fetchone()
    cursor.close()
    conn.close()

    return admin

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

def update_admin_profile(user_id, admin_name, phone):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
        UPDATE Admin
        SET admin_name=%s
        WHERE user_id=%s
        """,(admin_name,user_id))

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

