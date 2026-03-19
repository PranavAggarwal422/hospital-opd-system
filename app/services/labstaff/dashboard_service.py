from app.database.db import get_db_connection
 
def get_lab_dashboard_stats(lab_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT COUNT(*) total
        FROM TestRequest
        WHERE lab_id = %s
        AND test_status = 'Requested'
    """, (lab_id,))

    pending = cursor.fetchone()["total"]
    cursor.execute("""
        SELECT COUNT(*) total
        FROM TestRequest
        WHERE lab_id = %s
        AND test_status = 'SampleCollected'
    """, (lab_id,))

    collected = cursor.fetchone()["total"]

    cursor.execute("""
        SELECT COUNT(*) total
        FROM TestRequest
        WHERE lab_id = %s
        AND test_status = 'Completed'
        AND DATE(completed_time) = CURDATE()
    """, (lab_id,))

    completed_today = cursor.fetchone()["total"]

    cursor.close()
    conn.close()

    return {
        "pending": pending,
        "collected": collected,
        "completed_today": completed_today
    }

