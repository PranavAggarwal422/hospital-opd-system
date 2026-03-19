from app.database.db import get_db_connection


def get_staffs_by_lab(lab_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            ls.staff_id,
            ls.staff_name,
            ls.staff_role,
            ls.is_active,
            u.email,
            u.phone,
            u.user_status
        FROM LabStaff ls
        JOIN UserAccount u
            ON ls.user_id = u.user_id
        WHERE ls.lab_id = %s AND ls.is_active = TRUE
        ORDER BY ls.staff_name
    """, (lab_id,))

    staff = cursor.fetchall()

    cursor.close()
    conn.close()

    return staff

def get_staff_by_lab_id(staff_id, lab_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT staff_id
        FROM LabStaff
        WHERE staff_id=%s AND lab_id=%s
    """,(staff_id,lab_id))

    staff = cursor.fetchone()

    cursor.close()
    conn.close()

    return staff

def create_lab_staff(data):
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
            if user["user_role"] != "LabStaff":
                raise ValueError("Account exists but not Lab Staff")

            if user["user_status"] != "Inactive":
                raise ValueError("Lab Staff already active")

            # check lab staff record
            cursor.execute("""
                SELECT staff_id, staff_name
                FROM LabStaff
                WHERE user_id = %s
            """, (user_id,))

            lab_staff = cursor.fetchone()

            if lab_staff:
                if lab_staff["staff_name"] != data["staff_name"] :
                    raise ValueError("Lab Staff details do not match existing account")

                # reactivate lab staff
                cursor.execute("""
                    UPDATE LabStaff
                    SET is_active = TRUE,
                        lab_id = %s,
                        staff_role = %s
                    WHERE user_id = %s
                """, (
                    data["lab_id"],
                    data["staff_role"],
                    user_id
                ))

            else:
                # rare case: lab staff row missing
                cursor.execute("""
                    INSERT INTO LabStaff
                    (lab_id, user_id, staff_name, staff_role)
                    VALUES (%s,%s,%s,%s)
                """, (
                    data["lab_id"],
                    user_id,
                    data["staff_name"],
                    data["staff_role"]
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
                VALUES (%s,%s,%s,'LabStaff')
            """, (email, phone, data["password_hash"]))

            user_id = cursor.lastrowid


            cursor.execute("""
                INSERT INTO LabStaff
                (user_id, lab_id, staff_name, staff_role)
                VALUES (%s,%s,%s,%s)
            """, (
                user_id,
                data["lab_id"],
                data["staff_name"],
                data["staff_role"]
            ))


        conn.commit()

    except Exception:
        conn.rollback()
        raise

    finally:
        cursor.close()
        conn.close()

def deactivate_staff(staff_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT user_id
            FROM LabStaff
            WHERE staff_id = %s
        """, (staff_id,))

        result = cursor.fetchone()

        if not result:
            raise ValueError("Lab Staff not found")

        user_id = result[0]

        cursor.execute("""
            UPDATE LabStaff
            SET is_active = FALSE
            WHERE staff_id = %s
        """, (staff_id,))

        cursor.execute("""
            UPDATE UserAccount
            SET user_status = 'Inactive'
            WHERE user_id = %s
        """, (user_id,))

        conn.commit()

    except Exception:
        conn.rollback()
        raise

    finally:
        cursor.close()
        conn.close()


