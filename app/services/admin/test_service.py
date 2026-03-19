from app.database.db import get_db_connection
import mysql.connector

def get_tests_by_hospital(hospital_id, is_available = None):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if(is_available is None) : 
        cursor.execute("""
            SELECT
                test_id,
                test_name,
                test_type,
                test_description,
                is_available
            FROM HospitalTest
            WHERE hospital_id = %s
            ORDER BY is_available DESC,test_name 
        """, (hospital_id,))
    
    else : 
        cursor.execute("""
            SELECT
                test_id,
                test_name,
                test_type,
                test_description,
                is_available
            FROM HospitalTest
            WHERE hospital_id = %s AND is_available=%s
            ORDER BY test_name
        """, (hospital_id, is_available))

    tests = cursor.fetchall()

    cursor.close()
    conn.close()

    return tests

def get_test_by_hospital(test_id, hospital_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
    SELECT test_id, is_available
    FROM HospitalTest
    WHERE test_id=%s AND hospital_id=%s
    """,(test_id,hospital_id))

    test = cursor.fetchone()

    cursor.close()
    conn.close()

    return test

def create_hospital_test(data):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO HospitalTest
            (hospital_id, test_type, test_name, test_description)
            VALUES (%s,%s,%s,%s)
        """, (
            data["hospital_id"],
            data["test_type"],
            data["test_name"],
            data["test_description"]
        ))

        conn.commit()

    except mysql.connector.IntegrityError:
        conn.rollback()
        raise ValueError("Test already exists in this hospital")

    except Exception : 
        conn.rollback()
        raise 

    finally:
        cursor.close()
        conn.close()

def set_hospital_test_status(test_id, status):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # update hospital test status
        cursor.execute("""
            UPDATE HospitalTest
            SET is_available = %s
            WHERE test_id = %s
        """, (status, test_id))

        # if test is disabled, also disable it in all labs
        if not status:
            cursor.execute("""
                UPDATE LabSupportTest
                SET is_available = FALSE
                WHERE test_id = %s
            """, (test_id,))

        conn.commit()

    except Exception:
        conn.rollback()
        raise

    finally:
        cursor.close()
        conn.close()

def get_tests_by_lab(lab_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            ht.test_id,
            ht.test_name,
            ht.test_type,
            lst.is_available
        FROM LabSupportTest lst
        JOIN HospitalTest ht
            ON lst.test_id = ht.test_id
        WHERE lst.lab_id = %s
          AND lst.is_available = TRUE
          AND ht.is_available = TRUE
        ORDER BY ht.test_name
    """, (lab_id,))

    tests = cursor.fetchall()

    cursor.close()
    conn.close()

    return tests

def assign_test_to_lab(data):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary = True)

    try:
        cursor.execute("""
        SELECT is_available
        FROM LabSupportTest
        WHERE lab_id=%s AND test_id=%s
        """, (data["lab_id"], data["test_id"]))

        row = cursor.fetchone()

        if row:
            if row["is_available"] == True:
                raise ValueError("Test already assigned to this lab")
            cursor.execute("""
                UPDATE LabSupportTest
                SET is_available=TRUE
                WHERE lab_id=%s AND test_id=%s
            """, (data["lab_id"], data["test_id"]))
        else:
            cursor.execute("""
                INSERT INTO LabSupportTest (lab_id,test_id)
                VALUES (%s,%s)
            """, (data["lab_id"], data["test_id"]))
        
        conn.commit()

    except Exception:
        conn.rollback()
        raise 

    finally:
        cursor.close()
        conn.close()

def change_status_of_test_for_lab(lab_id, test_id, status):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE LabSupportTest
            SET is_available = %s
            WHERE lab_id = %s AND test_id = %s
        """, (status, lab_id, test_id))

        if cursor.rowcount == 0:
            raise ValueError("Test assignment not found")

        conn.commit()

    except Exception:
        conn.rollback()
        raise

    finally:
        cursor.close()
        conn.close()

def get_available_tests_for_lab(lab_id, hospital_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT ht.test_id, ht.test_name, ht.test_type
        FROM HospitalTest ht
        WHERE ht.hospital_id = %s
        AND ht.is_available = TRUE
        AND NOT EXISTS (
            SELECT 1
            FROM LabSupportTest lst
            WHERE lst.lab_id = %s
            AND lst.test_id = ht.test_id
            AND lst.is_available = TRUE
        )
        ORDER BY ht.test_name
    """, (hospital_id, lab_id))

    tests = cursor.fetchall()

    cursor.close()
    conn.close()

    return tests

