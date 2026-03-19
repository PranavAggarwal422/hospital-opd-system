from app.database.db import get_db_connection

def get_feedback_by_appointment(appointment_id, patient_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT f.feedback_id, f.rating, f.comment, f.submitted_time
        FROM Feedback f
        JOIN Appointment a
            ON f.appointment_id = a.appointment_id
        WHERE f.appointment_id = %s
        AND a.patient_id = %s
    """, (appointment_id, patient_id))

    feedback = cursor.fetchone()

    cursor.close()
    conn.close()

    return feedback

def submit_feedback(data):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO Feedback (appointment_id, rating, comment)
            VALUES (%s,%s,%s)
        """, (
            data["appointment_id"],
            data["rating"],
            data["comment"]
        ))

        conn.commit()

    except Exception:
        conn.rollback()
        raise

    finally:
        cursor.close()
        conn.close()


