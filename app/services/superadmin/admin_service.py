from app.database.db import get_db_connection


def create_admin(data):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        email = data["email"]
        phone = data["phone"]

        # check if user exists
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
            if user["user_role"] != "Admin":
                raise ValueError("Account already exists but not admin")

            if user["user_status"] != "Inactive"  : 
                raise ValueError("Account is already admin for a hospital")            

            # reactivate user and reset password 
            else : 
                cursor.execute("""
                    UPDATE UserAccount
                    SET user_status = 'Active', password_hash = %s, email = %s, phone = %s
                    WHERE user_id = %s
                """, (data["password_hash"], email, phone , user_id))

        else:
            cursor.execute("""
                INSERT INTO UserAccount
                (email, phone, password_hash, user_role)
                VALUES (%s, %s, %s, 'Admin')
            """, (email, phone, data["password_hash"]))

            user_id = cursor.lastrowid

        # user_id is unique ensured by database constraint 
        cursor.execute("""
            INSERT INTO Admin
            (user_id, hospital_id, admin_name)
            VALUES (%s, %s, %s)
        """, (
            user_id,
            data["hospital_id"],
            data["admin_name"]
        ))

        conn.commit()


    except Exception:
        conn.rollback()
        raise

    finally:
        cursor.close()
        conn.close()

def get_admins_by_hospital(hospital_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            a.admin_id,
            a.admin_name,
            u.email,
            u.phone,
            u.user_status
        FROM Admin a
        JOIN UserAccount u
            ON a.user_id = u.user_id
        WHERE a.hospital_id = %s
        ORDER BY a.admin_name
    """, (hospital_id,))

    admins = cursor.fetchall()

    cursor.close()
    conn.close()

    return admins

def deactivate_admin(admin_id):
    # delete from admin and set user to inactive
    conn = get_db_connection()
    cursor = conn.cursor()
    try : 
        cursor.execute("""
            SELECT user_id
            FROM Admin
            WHERE admin_id = %s
        """, (admin_id,))

        result = cursor.fetchone()
        if not result:
            raise ValueError("Admin not found")
        
        user_id = result[0]

        cursor.execute("""
            DELETE FROM Admin
            WHERE admin_id = %s
        """, (admin_id,))

        cursor.execute("""
            UPDATE UserAccount
            SET user_status = 'Inactive'
            WHERE user_id = %s
        """, (user_id,))

        conn.commit()
    
    except Exception : 
        conn.rollback()
        raise

    finally : 
        cursor.close()
        conn.close()

