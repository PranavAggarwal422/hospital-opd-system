from app.database.db import get_db_connection


def get_doctor_by_hospital_id(doctor_id, hospital_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT d.doctor_id
        FROM Doctor d
        JOIN Department dp ON d.department_id = dp.department_id
        WHERE d.doctor_id = %s AND dp.hospital_id = %s
    """, (doctor_id, hospital_id))

    doctor = cursor.fetchone()

    cursor.close()
    conn.close()

    return doctor

def get_doctors_by_department(department_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            d.doctor_id,
            d.doctor_name,
            d.gender,
            d.is_active,
            u.email,
            u.phone
        FROM Doctor d
        JOIN UserAccount u
            ON d.user_id = u.user_id
        WHERE d.department_id = %s AND d.is_active = TRUE
        ORDER BY d.doctor_name
    """, (department_id,))

    doctors = cursor.fetchall()

    cursor.close()
    conn.close()

    return doctors

def create_doctor(data):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        email = data["email"]
        phone = data["phone"]

        # find matching users
        cursor.execute("""
            SELECT user_id, user_role, user_status
            FROM UserAccount
            WHERE email = %s OR phone = %s
        """, (email, phone))

        users = cursor.fetchall()

        if len(users) > 1:
            raise ValueError("Email and phone belong to different accounts")

        user = users[0] if users else None

        if user:
            user_id = user["user_id"]
            if user["user_role"] != "Doctor":
                raise ValueError("Account exists but not doctor")

            if user["user_status"] != "Inactive":
                raise ValueError("Doctor already active")

            # check doctor record
            cursor.execute("""
                SELECT doctor_id, doctor_name, gender
                FROM Doctor
                WHERE user_id = %s
            """, (user_id,))

            doctor = cursor.fetchone()

            if doctor:
                if doctor["doctor_name"] != data["doctor_name"] or doctor["gender"] != data["gender"]:
                    raise ValueError("Doctor details do not match existing account")

                # reactivate doctor
                cursor.execute("""
                    UPDATE Doctor
                    SET is_active = TRUE,
                        department_id = %s
                    WHERE user_id = %s
                """, (
                    data["department_id"],
                    user_id
                ))

            else:
                # rare case: doctor row missing
                cursor.execute("""
                    INSERT INTO Doctor
                    (user_id, department_id, doctor_name, gender)
                    VALUES (%s,%s,%s,%s)
                """, (
                    user_id,
                    data["department_id"],
                    data["doctor_name"],
                    data["gender"]
                ))


            # reactivate user account
            cursor.execute("""
                UPDATE UserAccount
                SET user_status = 'Active',
                    password_hash = %s,
                    email = %s, 
                    phone = %s
                WHERE user_id = %s
            """, (data["password_hash"], email, phone, user_id))

        else:
            # create new user
            cursor.execute("""
                INSERT INTO UserAccount
                (email, phone, password_hash, user_role)
                VALUES (%s,%s,%s,'Doctor')
            """, (email, phone, data["password_hash"]))

            user_id = cursor.lastrowid


            cursor.execute("""
                INSERT INTO Doctor
                (user_id, department_id, doctor_name, gender)
                VALUES (%s,%s,%s,%s)
            """, (
                user_id,
                data["department_id"],
                data["doctor_name"],
                data["gender"]
            ))


        conn.commit()

    except Exception:
        conn.rollback()
        raise

    finally:
        cursor.close()
        conn.close()

def deactivate_doctor(doctor_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT user_id
            FROM Doctor
            WHERE doctor_id = %s
        """, (doctor_id,))

        result = cursor.fetchone()

        if not result:
            raise ValueError("Doctor not found")

        user_id = result[0]
        
        # Deactivate Doctor
        cursor.execute("""
            UPDATE Doctor
            SET is_active = FALSE
            WHERE doctor_id = %s
        """, (doctor_id,))

        # Deactivate User Account
        cursor.execute("""
            UPDATE UserAccount
            SET user_status = 'Inactive'
            WHERE user_id = %s
        """, (user_id,))

        # Deactivate Sessions 
        cursor.execute("""
            UPDATE OPDSession
            SET is_active = FALSE
            WHERE doctor_id = %s
        """, (doctor_id,))

        conn.commit()

    except Exception:
        conn.rollback()
        raise

    finally:
        cursor.close()
        conn.close()


