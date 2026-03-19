from app.database.db import get_db_connection
import mysql.connector


def get_departments_by_hospital(hospital_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT department_id, department_name, is_active
        FROM Department
        WHERE hospital_id = %s
        ORDER BY is_active DESC, department_name
    """, (hospital_id,))

    departments = cursor.fetchall()

    cursor.close()
    conn.close()

    return departments

def get_department_by_hospital(department_id, hospital_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT department_id, department_name, is_active
        FROM Department
        WHERE department_id = %s
        AND hospital_id = %s
    """, (department_id, hospital_id))

    department = cursor.fetchone()

    cursor.close()
    conn.close()

    return department

def create_department(data):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO Department
            (department_name, hospital_id)
            VALUES (%s, %s)
        """, (data["department_name"], data["hospital_id"]))

        conn.commit()

    except mysql.connector.IntegrityError:
        conn.rollback()
        raise ValueError("Department already exists")

    except Exception:
        conn.rollback()
        raise

    finally:
        cursor.close()
        conn.close()

def deactivate_department(department_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # check active doctors
        cursor.execute("""
            SELECT COUNT(*) FROM Doctor
            WHERE department_id = %s AND is_active = TRUE
        """, (department_id,))
        active_doctors = cursor.fetchone()[0]

        if active_doctors > 0:
            raise ValueError(f"Cannot deactivate department. {active_doctors} active doctor(s) exist.")

        # check active OPDs
        cursor.execute("""
            SELECT COUNT(*) FROM OPD
            WHERE department_id = %s AND is_active = TRUE
        """, (department_id,))
        active_opds = cursor.fetchone()[0]

        if active_opds > 0:
            raise ValueError(f"Cannot deactivate department. {active_opds} active OPD room(s) exist.")

        # safe to deactivate
        cursor.execute("""
            UPDATE Department
            SET is_active = FALSE
            WHERE department_id = %s
        """, (department_id,))

        conn.commit()

    except Exception:
        conn.rollback()
        raise

    finally:
        cursor.close()
        conn.close()

def activate_department(department_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            UPDATE Department
            SET is_active = TRUE
            WHERE department_id = %s
        """, (department_id,))

        conn.commit()

    except Exception:
        conn.rollback()
        raise

    finally:
        cursor.close()
        conn.close()


