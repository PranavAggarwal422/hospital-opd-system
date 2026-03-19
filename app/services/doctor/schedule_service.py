from app.database.db import get_db_connection

def get_doctor_schedule(user_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            s.week_day,
            s.start_time,
            s.end_time,
            s.max_tokens_per_session,
            o.room_no,
            d.department_name
        FROM OPDSession s

        JOIN Doctor doc
            ON s.doctor_id = doc.doctor_id

        JOIN OPD o
            ON s.opd_id = o.opd_id

        JOIN Department d
            ON o.department_id = d.department_id

        WHERE doc.user_id = %s
          AND s.is_active = TRUE

        ORDER BY
            FIELD(
                s.week_day,
                'Monday','Tuesday','Wednesday','Thursday',
                'Friday','Saturday','Sunday'
            ),
            s.start_time
    """, (user_id,))

    schedule = cursor.fetchall()

    cursor.close()
    conn.close()

    return schedule

