from app.database.db import get_db_connection 
import mysql.connector 

def get_user_by_email(value) : 
    conn = get_db_connection()  
    cursor = conn.cursor(dictionary = True)

    query = """
    SELECT user_id, email, phone, password_hash, user_role, user_status
    FROM UserAccount
    WHERE email = %s
    """

    cursor.execute(query, (value,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return user


def get_user_by_id(value) : 
    conn = get_db_connection()  
    cursor = conn.cursor(dictionary = True)

    query = """
    SELECT user_id, email, phone, password_hash, user_role, user_status
    FROM UserAccount
    WHERE user_id = %s
    """

    cursor.execute(query, (value,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return user


def get_user_by_phone(value) : 
    conn = get_db_connection()  
    cursor = conn.cursor(dictionary = True)

    query = """
    SELECT user_id, email, phone, password_hash, user_role, user_status
    FROM UserAccount
    WHERE phone = %s
    """

    cursor.execute(query, (value,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return user

def register_patient(data):
    conn = get_db_connection()
    cursor = conn.cursor()
    try :
        # insert user
        user_query = """
        INSERT INTO UserAccount (email, phone, password_hash, user_role)
        VALUES (%s, %s, %s, 'Patient')
        """

        cursor.execute(user_query, (data["email"], data["phone"], data["password_hash"]))
        user_id = cursor.lastrowid

        # insert patient
        patient_query = """
        INSERT INTO Patient (user_id, patient_name, gender, dob, address)
        VALUES (%s, %s, %s, %s, %s)
        """

        cursor.execute(patient_query, (user_id,data["patient_name"], data["gender"], data["dob"], data["address"]))

        conn.commit()
        return user_id

    except mysql.connector.IntegrityError : 
        conn.rollback()
        raise ValueError("Account already exists. Please login.")

    except Exception:
        conn.rollback()
        raise
        
    finally : 
        cursor.close()
        conn.close()


def update_user_password(user_id, password_hash):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
        UPDATE UserAccount
        SET password_hash=%s
        WHERE user_id=%s
        """,(password_hash,user_id))

        conn.commit()

    finally:
        cursor.close()
        conn.close()