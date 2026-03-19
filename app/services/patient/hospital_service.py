from app.database.db import get_db_connection

def get_active_hospitals(search=None):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        if search:
            query = """
                SELECT hospital_id, hospital_name, city, state
                FROM Hospital
                WHERE is_active = TRUE
                AND (
                    hospital_name LIKE %s
                    OR city LIKE %s
                    OR state LIKE %s
                )
                ORDER BY hospital_name ASC
            """
            like = f"%{search}%"
            cursor.execute(query, (like, like, like))
        else:
            query = """
                SELECT hospital_id, hospital_name, city, state
                FROM Hospital
                WHERE is_active = TRUE
                ORDER BY hospital_name ASC
            """
            cursor.execute(query)

        hospitals = cursor.fetchall()
        return hospitals

    except Exception as e:
        raise

    finally:
        cursor.close()
        conn.close()

def get_departments_by_hospital(hospital_id, search=None):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        if search:
            query = """
                SELECT department_id, department_name
                FROM Department
                WHERE hospital_id = %s
                AND is_active = TRUE
                AND department_name LIKE %s
                ORDER BY department_name ASC
            """
            like = f"%{search}%"
            cursor.execute(query, (hospital_id, like))
        else:
            query = """
                SELECT department_id, department_name
                FROM Department
                WHERE hospital_id = %s
                AND is_active = TRUE
                ORDER BY department_name ASC
            """
            cursor.execute(query, (hospital_id,))

        return cursor.fetchall()

    except Exception as e:
        raise

    finally:
        cursor.close()
        conn.close()


