from flask import current_app
from werkzeug.utils import secure_filename
import os
import uuid
from app.database.db import get_db_connection




def upload_report(data):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
        SELECT test_status
        FROM TestRequest
        WHERE request_id=%s
        """, (data["request_id"],))
        req = cursor.fetchone()
        if not req:
            raise ValueError("Test request not found")
        if req["test_status"] != "SampleCollected":
            raise ValueError("Report can only be uploaded after sample collection")
        
        cursor.execute("""
        SELECT request_id FROM Report WHERE request_id = %s
        """, (data["request_id"],))
        if cursor.fetchone():
            raise ValueError("Report already uploaded for this test request.")
                     
        cursor.execute("""
            INSERT INTO Report
            (request_id, report_url, remarks)
            VALUES (%s,%s,%s)
        """, (
            data["request_id"],
            data["report_url"],
            data["remarks"]
        ))

        cursor.execute("""
            UPDATE TestRequest
            SET test_status = 'Completed',
                completed_time = NOW()
            WHERE request_id = %s
        """, (data["request_id"],))

        conn.commit()

        

    except Exception:
        conn.rollback()
        raise

    finally:
        cursor.close()
        conn.close()

ALLOWED_EXTENSIONS = {"pdf", "png", "jpg", "jpeg"}
def allowed_file(filename):
    if "." not in filename:
        return False
    ext = filename.rsplit(".", 1)[1].lower()
    return ext in ALLOWED_EXTENSIONS


def save_report_file(file):
    if not file or file.filename == "":
        raise ValueError("No file selected")
    if not allowed_file(file.filename):
        raise ValueError("Only PDF, PNG, JPG, JPEG files are allowed")


    file.seek(0, os.SEEK_END)
    size = file.tell()
    file.seek(0)
    if size > 5 * 1024 * 1024:
        raise ValueError("File size must be less than 5MB")

    upload_folder = current_app.config["UPLOAD_FOLDER"]
    os.makedirs(upload_folder, exist_ok=True)
    filename = str(uuid.uuid4()) + "_" + secure_filename(file.filename)
    filepath = os.path.join(upload_folder, filename)
    file.save(filepath)

    return filename
