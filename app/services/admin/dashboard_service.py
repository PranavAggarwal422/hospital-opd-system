from app.database.db import get_db_connection

def get_admin_dashboard_stats(hospital_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
    SELECT COUNT(*) total FROM Department
    WHERE hospital_id=%s AND is_active=TRUE
    """,(hospital_id,))
    departments = cursor.fetchone()["total"]

    cursor.execute("""
    SELECT COUNT(*) total
    FROM Doctor d
    JOIN Department dp ON d.department_id = dp.department_id
    WHERE dp.hospital_id=%s AND d.is_active=TRUE
    """,(hospital_id,))
    doctors = cursor.fetchone()["total"]

    cursor.execute("""
    SELECT COUNT(*) total
    FROM OPD
    WHERE hospital_id=%s AND is_active=TRUE
    """,(hospital_id,))
    opds = cursor.fetchone()["total"]

    cursor.execute("""
    SELECT COUNT(*) total
    FROM OPDSession s
    JOIN OPD o ON s.opd_id=o.opd_id
    WHERE o.hospital_id=%s AND s.is_active=TRUE
    """,(hospital_id,))
    sessions = cursor.fetchone()["total"]

    cursor.execute("""
    SELECT COUNT(*) total
    FROM DiagnosticLab
    WHERE hospital_id=%s AND is_active=TRUE
    """,(hospital_id,))
    labs = cursor.fetchone()["total"]

    cursor.execute("""
    SELECT COUNT(*) total
    FROM LabStaff ls
    JOIN DiagnosticLab dl ON ls.lab_id = dl.lab_id
    WHERE dl.hospital_id=%s AND ls.is_active=TRUE
    """,(hospital_id,))
    staff = cursor.fetchone()["total"]

    cursor.execute("""
    SELECT COUNT(*) total
    FROM HospitalTest
    WHERE hospital_id=%s AND is_available=TRUE
    """,(hospital_id,))
    tests = cursor.fetchone()["total"]

    cursor.close()
    conn.close()

    return {
        "departments":departments,
        "doctors":doctors,
        "opds":opds,
        "sessions":sessions,
        "labs":labs,
        "staff":staff,
        "tests":tests
    }
    
