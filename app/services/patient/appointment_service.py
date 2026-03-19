from app.database.db import get_db_connection
from datetime import datetime

def get_sessions_by_department(department_id, search=None):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        if search:
            query = """
                SELECT
                    s.session_id,
                    s.week_day,
                    s.start_time,
                    s.end_time,
                    s.max_tokens_per_session,

                    d.doctor_name,
                    o.room_no,
                    h.hospital_name

                FROM OPDSession s

                JOIN Doctor d
                    ON s.doctor_id = d.doctor_id

                JOIN OPD o
                    ON s.opd_id = o.opd_id

                JOIN Hospital h
                    ON o.hospital_id = h.hospital_id

                WHERE o.department_id = %s
                AND s.is_active = TRUE
                AND d.is_active = TRUE
                AND o.is_active = TRUE
                AND (
                    d.doctor_name LIKE %s
                    OR s.week_day LIKE %s
                )

                ORDER BY FIELD(s.week_day,'Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'),s.start_time
            """

            like = f"%{search}%"
            cursor.execute(query, (department_id, like, like))

        else:
            query = """
                SELECT
                    s.session_id,
                    s.week_day,
                    s.start_time,
                    s.end_time,
                    s.max_tokens_per_session,

                    d.doctor_name,
                    o.room_no,
                    h.hospital_name

                FROM OPDSession s

                JOIN Doctor d
                    ON s.doctor_id = d.doctor_id

                JOIN OPD o
                    ON s.opd_id = o.opd_id

                JOIN Hospital h
                    ON o.hospital_id = h.hospital_id

                WHERE o.department_id = %s
                AND s.is_active = TRUE
                AND d.is_active = TRUE
                AND o.is_active = TRUE

                ORDER BY FIELD(s.week_day,'Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'),
                         s.start_time
            """

            cursor.execute(query, (department_id,))

        sessions = cursor.fetchall()
        return sessions

    except Exception as e:
        raise

    finally:
        cursor.close()
        conn.close()


def book_appointment(data):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # Fetch complete session context
        cursor.execute("""
            SELECT
                s.week_day,
                s.start_time,
                s.end_time,
                s.is_active AS session_active,

                o.department_id,
                o.is_active AS opd_active,

                d.is_active AS doctor_active,

                dp.is_active AS department_active,

                h.is_active AS hospital_active

            FROM OPDSession s
            JOIN OPD o ON s.opd_id = o.opd_id
            JOIN Doctor d ON s.doctor_id = d.doctor_id
            JOIN Department dp ON o.department_id = dp.department_id
            JOIN Hospital h ON o.hospital_id = h.hospital_id

            WHERE s.session_id = %s
        """, (data["session_id"],))

        session = cursor.fetchone()

        if not session:
            raise ValueError("Invalid session selected.")

        if not session["hospital_active"]:
            raise ValueError("Hospital is currently inactive.")

        if not session["department_active"]:
            raise ValueError("Department is currently inactive.")

        if not session["opd_active"]:
            raise ValueError("This OPD room is currently inactive.")

        if not session["doctor_active"]:
            raise ValueError("Doctor is not currently available.")

        if not session["session_active"]:
            raise ValueError("This session is no longer available.")

        department_id = session["department_id"]
        appointment_date = data["appointment_date"]

        today = datetime.today().date()

        # Prevent past booking
        if appointment_date < today:
            raise ValueError("Cannot book appointment in the past.")

        # Prevent booking too far in future (30 days)
        if (appointment_date - today).days > 30:
            raise ValueError("Appointments can only be booked within the next 30 days.")

        # Validate weekday
        weekday_map = {
            0: "Monday",
            1: "Tuesday",
            2: "Wednesday",
            3: "Thursday",
            4: "Friday",
            5: "Saturday",
            6: "Sunday"
        }

        appointment_day = weekday_map[appointment_date.weekday()]

        if appointment_day != session["week_day"]:
            raise ValueError(f"This session is only available on {session['week_day']}.")

        # Prevent booking if today's session ended
        if appointment_date == today:

            cursor.execute("SELECT CURTIME() AS now")
            now = cursor.fetchone()["now"]

            if now > session["end_time"]:
                raise ValueError("This OPD session has already ended for today.")
            
        # Prevent rebooking cancelled appointments
        cursor.execute("""
            SELECT appointment_status
            FROM Appointment
            WHERE patient_id = %s
            AND department_id = %s
            AND appointment_date = %s
            LIMIT 1
        """, (
            data["patient_id"],
            department_id,
            appointment_date
        ))

        existing_same_day = cursor.fetchone()

        if existing_same_day:
            if existing_same_day["appointment_status"] == "Cancelled":
                raise ValueError(
                    f"You already had an appointment for this department on {appointment_date} and cancelled it. "
                    "Rebooking for the same day is not allowed."
                )
            else:
                raise ValueError(f"You already have an appointment in this department on {existing['appointment_date']}.")

        # Prevent multiple upcoming appointments in same department
        cursor.execute("""
            SELECT appointment_date
            FROM Appointment
            WHERE patient_id = %s
            AND department_id = %s
            AND appointment_status = 'Booked'
            AND appointment_date >= CURDATE()
            ORDER BY appointment_date
            LIMIT 1
        """, (
            data["patient_id"],
            department_id
        ))

        existing = cursor.fetchone()

        if existing:
            raise ValueError(f"You already have an upcoming appointment in this department on {existing['appointment_date']}.")

        # Insert appointment
        cursor.execute("""
        INSERT INTO Appointment
        (session_id, patient_id, department_id, appointment_date)
        VALUES (%s,%s,%s,%s)
        """, (
            data["session_id"],
            data["patient_id"],
            department_id,
            appointment_date
        ))

        conn.commit()

    except Exception:
        conn.rollback()
        raise

    finally:
        cursor.close()
        conn.close()

# patient appointment history
def get_patient_appointments(patient_id, search=None):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        if search:
            query = """
                SELECT
                    a.appointment_id,
                    a.token_no,
                    a.appointment_date,
                    a.appointment_status,

                    d.doctor_name,
                    s.start_time,
                    s.end_time,

                    h.hospital_name,
                    dp.department_name

                FROM Appointment a

                JOIN OPDSession s
                    ON a.session_id = s.session_id

                JOIN Doctor d
                    ON s.doctor_id = d.doctor_id

                JOIN OPD o
                    ON s.opd_id = o.opd_id

                JOIN Hospital h
                    ON o.hospital_id = h.hospital_id

                JOIN Department dp
                    ON a.department_id = dp.department_id

                WHERE a.patient_id = %s
                AND (
                    d.doctor_name LIKE %s
                    OR h.hospital_name LIKE %s
                    OR dp.department_name LIKE %s
                )

                ORDER BY a.appointment_date DESC
            """

            like = f"%{search}%"
            cursor.execute(query, (patient_id, like, like, like))

        else:
            query = """
                SELECT
                    a.appointment_id,
                    a.token_no,
                    a.appointment_date,
                    a.appointment_status,

                    d.doctor_name,
                    s.start_time,
                    s.end_time,

                    h.hospital_name,
                    dp.department_name

                FROM Appointment a

                JOIN OPDSession s
                    ON a.session_id = s.session_id

                JOIN Doctor d
                    ON s.doctor_id = d.doctor_id

                JOIN OPD o
                    ON s.opd_id = o.opd_id

                JOIN Hospital h
                    ON o.hospital_id = h.hospital_id

                JOIN Department dp
                    ON a.department_id = dp.department_id

                WHERE a.patient_id = %s

                ORDER BY a.appointment_date DESC
            """

            cursor.execute(query, (patient_id,))

        return cursor.fetchall()

    except Exception as e:
        print(f"[ERROR] get_patient_appointments: {str(e)}")
        raise

    finally:
        cursor.close()
        conn.close()

            
# patient upcoming appointments
def get_upcoming_appointments(patient_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            a.appointment_id,
            a.token_no,
            a.appointment_date,

            d.doctor_name,
            s.start_time,
            s.end_time,

            -- Expected arrival time
            ADDTIME(
                s.start_time,
                SEC_TO_TIME((a.token_no - 1) * 300)
            ) AS expected_time,

            h.hospital_name,
            dp.department_name

        FROM Appointment a

        JOIN OPDSession s
            ON a.session_id = s.session_id

        JOIN Doctor d
            ON s.doctor_id = d.doctor_id

        JOIN OPD o
            ON s.opd_id = o.opd_id

        JOIN Hospital h
            ON o.hospital_id = h.hospital_id

        JOIN Department dp
            ON a.department_id = dp.department_id

        WHERE a.patient_id = %s
        AND a.appointment_status = 'Booked'

        AND (
            a.appointment_date > CURDATE()
            OR
            (
                a.appointment_date = CURDATE()
                AND s.end_time >= CURTIME()
            )
        )

        ORDER BY a.appointment_date ASC, s.start_time ASC, a.token_no ASC
    """, (patient_id,))

    appointments = cursor.fetchall()

    cursor.close()
    conn.close()

    return appointments

def cancel_appointment(appointment_id, patient_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT appointment_status, appointment_date
            FROM Appointment
            WHERE appointment_id = %s
            AND patient_id = %s
        """, (appointment_id, patient_id))

        appointment = cursor.fetchone()

        if not appointment:
            raise ValueError("Appointment not found")

        if appointment["appointment_status"] != "Booked":
            raise ValueError("This appointment cannot be cancelled")

        # Prevent cancelling past appointments
        cursor.execute("SELECT CURDATE() AS today")
        today = cursor.fetchone()["today"]

        if appointment["appointment_date"] < today:
            raise ValueError("Past appointments cannot be cancelled")

        cursor.execute("""
            UPDATE Appointment
            SET appointment_status = 'Cancelled'
            WHERE appointment_id = %s
        """, (appointment_id,))

        conn.commit()

    except Exception:
        conn.rollback()
        raise

    finally:
        cursor.close()
        conn.close()

def get_appointment_details(appointment_id, patient_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            a.appointment_id,
            a.token_no,
            a.appointment_date,
            a.appointment_status,

            d.doctor_name,

            s.start_time,
            s.end_time,

            o.room_no,

            h.hospital_name,
            h.city,
            h.state,

            dp.department_name,

            ADDTIME(
                s.start_time,
                SEC_TO_TIME((a.token_no - 1) * 300)
            ) AS expected_time

        FROM Appointment a

        JOIN OPDSession s
            ON a.session_id = s.session_id

        JOIN Doctor d
            ON s.doctor_id = d.doctor_id

        JOIN OPD o
            ON s.opd_id = o.opd_id

        JOIN Hospital h
            ON o.hospital_id = h.hospital_id

        JOIN Department dp
            ON a.department_id = dp.department_id

        WHERE a.appointment_id = %s
        AND a.patient_id = %s
    """, (appointment_id, patient_id))

    appointment = cursor.fetchone()

    cursor.close()
    conn.close()

    return appointment

def get_tests_of_appointment(appointment_id, patient_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Verify appointment belongs to patient
    cursor.execute("""
        SELECT appointment_id
        FROM Appointment
        WHERE appointment_id = %s
        AND patient_id = %s
    """, (appointment_id, patient_id))

    appointment = cursor.fetchone()

    if not appointment:
        cursor.close()
        conn.close()
        return None

    cursor.execute("""
        SELECT
            tr.request_id,
            ht.test_name,
            ht.test_type,
            tr.test_status,
            tr.sample_collected_time,
            tr.completed_time,
            r.report_url,
            r.remarks

        FROM TestRequest tr

        JOIN HospitalTest ht
            ON tr.test_id = ht.test_id

        LEFT JOIN Report r
            ON tr.request_id = r.request_id

        WHERE tr.appointment_id = %s

        ORDER BY ht.test_name
    """, (appointment_id,))

    tests = cursor.fetchall()

    cursor.close()
    conn.close()

    return tests

