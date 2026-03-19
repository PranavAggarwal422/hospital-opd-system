from app.database.db import get_db_connection


def get_recent_reports(patient_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            ht.test_name,
            ht.test_type,
            r.report_url,
            tr.completed_time,
            tr.request_id,
            h.hospital_name
        FROM Report r
        JOIN TestRequest tr
            ON r.request_id = tr.request_id
        JOIN HospitalTest ht
            ON tr.test_id = ht.test_id
        JOIN Appointment a
            ON tr.appointment_id = a.appointment_id
        JOIN OPDSession s
            ON a.session_id = s.session_id
        JOIN OPD o
            ON s.opd_id = o.opd_id
        JOIN Hospital h
            ON o.hospital_id = h.hospital_id
        WHERE a.patient_id = %s 
        ORDER BY tr.completed_time DESC
        LIMIT 5
    """, (patient_id,))

    reports = cursor.fetchall()

    cursor.close()
    conn.close()

    return reports

def get_all_reports(patient_id, search=None):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        if search:
            query = """
                SELECT
                    ht.test_name,
                    ht.test_type,
                    r.report_url,
                    r.remarks,
                    tr.completed_time,
                    tr.request_id,
                    h.hospital_name

                FROM Report r

                JOIN TestRequest tr
                    ON r.request_id = tr.request_id

                JOIN HospitalTest ht
                    ON tr.test_id = ht.test_id

                JOIN Appointment a
                    ON tr.appointment_id = a.appointment_id

                JOIN OPDSession s
                    ON a.session_id = s.session_id

                JOIN OPD o
                    ON s.opd_id = o.opd_id

                JOIN Hospital h
                    ON o.hospital_id = h.hospital_id

                WHERE a.patient_id = %s
                AND (
                    ht.test_name LIKE %s
                    OR ht.test_type LIKE %s
                    OR h.hospital_name LIKE %s
                )

                ORDER BY tr.completed_time DESC
            """

            like = f"%{search}%"
            cursor.execute(query, (patient_id, like, like, like))

        else:
            query = """
                SELECT
                    ht.test_name,
                    ht.test_type,
                    r.report_url,
                    r.remarks,
                    tr.completed_time,
                    tr.request_id,
                    h.hospital_name

                FROM Report r

                JOIN TestRequest tr
                    ON r.request_id = tr.request_id

                JOIN HospitalTest ht
                    ON tr.test_id = ht.test_id

                JOIN Appointment a
                    ON tr.appointment_id = a.appointment_id

                JOIN OPDSession s
                    ON a.session_id = s.session_id

                JOIN OPD o
                    ON s.opd_id = o.opd_id

                JOIN Hospital h
                    ON o.hospital_id = h.hospital_id

                WHERE a.patient_id = %s

                ORDER BY tr.completed_time DESC
            """

            cursor.execute(query, (patient_id,))

        return cursor.fetchall()

    except Exception as e:
        raise

    finally:
        cursor.close()
        conn.close()


def get_report_by_request(request_id, patient_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT r.report_url
        FROM Report r
        JOIN TestRequest tr ON r.request_id = tr.request_id
        JOIN Appointment a ON tr.appointment_id = a.appointment_id
        WHERE tr.request_id = %s
        AND a.patient_id = %s
    """, (request_id, patient_id))

    result = cursor.fetchone()

    cursor.close()
    conn.close()

    return result

