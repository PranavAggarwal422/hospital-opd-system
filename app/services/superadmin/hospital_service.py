from app.database.db import get_db_connection
import mysql.connector 

def get_all_hospitals():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT hospital_id, hospital_name, city, state, pincode, is_active
        FROM Hospital
        ORDER BY state, city, is_active DESC, hospital_name
    """)

    hospitals = cursor.fetchall()
    cursor.close()
    conn.close()
    return hospitals

def get_active_hospitals():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT hospital_id, hospital_name
        FROM Hospital
        WHERE is_active = TRUE
        ORDER BY hospital_name
    """)

    hospitals = cursor.fetchall()

    cursor.close()
    conn.close()

    return hospitals

def get_hospital(hospital_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT hospital_id, hospital_name, city, state, pincode, is_active
        FROM Hospital
        WHERE hospital_id = %s
    """, (hospital_id,))

    hospital = cursor.fetchone()

    cursor.close()
    conn.close()

    return hospital

def create_hospital(data):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        query = """
        INSERT INTO Hospital
        (hospital_name, address, city, state, pincode)
        VALUES (%s, %s, %s, %s, %s)
        """

        cursor.execute(query, (data["hospital_name"], data["address"], data["city"], data["state"], data["pincode"]))

        conn.commit()


    except mysql.connector.IntegrityError:
        conn.rollback()
        raise ValueError("Hospital already exists")

    except Exception:
        conn.rollback()
        raise

    finally:
        cursor.close()
        conn.close()

def deactivate_hospital(hospital_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            UPDATE Hospital
            SET is_active = FALSE
            WHERE hospital_id = %s
        """, (hospital_id,))

        conn.commit()

    except Exception:
        conn.rollback()
        raise

    finally:
        cursor.close()
        conn.close()
    
def activate_hospital(hospital_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            UPDATE Hospital
            SET is_active = TRUE
            WHERE hospital_id = %s
        """, (hospital_id,))

        conn.commit()

    except Exception:
        conn.rollback()
        raise

    finally:
        cursor.close()
        conn.close()


