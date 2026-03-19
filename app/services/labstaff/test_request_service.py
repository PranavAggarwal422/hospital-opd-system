from app.database.db import get_db_connection
from datetime import date 


def get_tests_supported_by_lab(lab_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT ht.test_id, ht.test_name
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

    return [(t["test_id"], t["test_name"]) for t in tests]

def get_lab_test_requests(lab_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            tr.request_id,
            tr.test_status,
            tr.sample_collected_time,
            tr.completed_time,

            ht.test_name,
            ht.test_type,

            a.appointment_id,
            a.token_no,
            a.appointment_date,

            p.patient_name

        FROM TestRequest tr

        JOIN HospitalTest ht
            ON tr.test_id = ht.test_id

        JOIN Appointment a
            ON tr.appointment_id = a.appointment_id

        JOIN Patient p
            ON a.patient_id = p.patient_id

        WHERE tr.lab_id = %s

        ORDER BY FIELD(tr.test_status,'Requested','SampleCollected','Completed'), tr.request_id DESC
    """, (lab_id,))

    tests = cursor.fetchall()

    cursor.close()
    conn.close()

    return tests

def create_test_request(data):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # find appointment using patient contact + department + date
        cursor.execute("""
            SELECT
                a.appointment_id,
                a.appointment_status,
                s.start_time,
                s.end_time,
                a.appointment_date
            FROM Appointment a
            JOIN OPDSession s
                ON a.session_id = s.session_id
            JOIN Patient p
                ON a.patient_id = p.patient_id
            JOIN UserAccount u
                ON p.user_id = u.user_id
            WHERE (u.email = %s OR u.phone = %s)
            AND a.department_id = %s
            AND a.appointment_date = %s
        """, (
            data["email_or_phone"],
            data["email_or_phone"],
            data["department_id"],
            data["appointment_date"]
        ))

        appointment = cursor.fetchone()
        if not appointment:
            raise ValueError("No appointment found for this patient")

        
        today = date.today()
        if appointment["appointment_date"] > today:
            raise ValueError("Test request cannot be created before the appointment date")
        
        if appointment["appointment_date"] == today:
            cursor.execute("SELECT CURTIME() AS now")
            now = cursor.fetchone()["now"]
            if now < appointment["start_time"]:
                raise ValueError("Patient appointment has not started yet")

        if appointment["appointment_status"] == "Cancelled":
            raise ValueError("Test cannot be created for cancelled appointments")

        appointment_id = appointment["appointment_id"]

        # verify test supported by lab
        cursor.execute("""
            SELECT test_id
            FROM LabSupportTest
            WHERE lab_id = %s
            AND test_id = %s
            AND is_available = TRUE
        """, (data["lab_id"], data["test_id"]))

        supported = cursor.fetchone()

        if not supported:
            raise ValueError("This test is not supported by this lab")

        # prevent duplicate request
        cursor.execute("""
            SELECT request_id
            FROM TestRequest
            WHERE appointment_id = %s
            AND test_id = %s
        """, (appointment_id, data["test_id"]))

        existing = cursor.fetchone()

        if existing:
            raise ValueError("Test request already exists")

        cursor.execute("""
            INSERT INTO TestRequest
            (appointment_id, test_id, lab_id)
            VALUES (%s,%s,%s)
        """, (
            appointment_id,
            data["test_id"],
            data["lab_id"]
        ))

        conn.commit()

    except Exception:
        conn.rollback()
        raise

    finally:
        cursor.close()
        conn.close()

def collect_sample(request_id, lab_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT test_status
            FROM TestRequest
            WHERE request_id = %s
            AND lab_id = %s
        """, (request_id, lab_id))

        request_data = cursor.fetchone()

        if not request_data:
            raise ValueError("Test request not found")
        
        if request_data["test_status"] == "Completed":
            raise ValueError("Test already completed")

        if request_data["test_status"] != "Requested":
            raise ValueError("Sample already collected")

        cursor.execute("""
            UPDATE TestRequest
            SET test_status = 'SampleCollected',
                sample_collected_time = NOW()
            WHERE request_id = %s
        """, (request_id,))

        conn.commit()

    except Exception:
        conn.rollback()
        raise

    finally:
        cursor.close()
        conn.close()

def get_test_request_by_id(request_id, lab_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            tr.request_id,
            tr.test_status,
            ht.test_name
        FROM TestRequest tr
        JOIN HospitalTest ht
            ON tr.test_id = ht.test_id
        WHERE tr.request_id = %s
        AND tr.lab_id = %s
    """, (request_id, lab_id))

    request_data = cursor.fetchone()

    cursor.close()
    conn.close()

    return request_data

def get_departments_of_lab_hospital(lab_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT d.department_id, d.department_name
        FROM Department d
        JOIN DiagnosticLab l
            ON d.hospital_id = l.hospital_id
        WHERE l.lab_id = %s
        AND d.is_active = TRUE
        ORDER BY d.department_name
    """, (lab_id,))

    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return [(r["department_id"], r["department_name"]) for r in rows]

