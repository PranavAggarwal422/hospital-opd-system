from flask import Flask  
from flask_bcrypt import Bcrypt 
from flask_login import LoginManager, UserMixin
from .config import Config 
from app.database.db import get_db_connection

bcrypt = Bcrypt()
login_manager = LoginManager()

class User(UserMixin):
    def __init__(self, user_data):
        self.id = user_data["user_id"]
        self.user_role = user_data["user_role"]
        self.hospital_id = user_data.get("hospital_id")
        self.hospital_name = user_data.get("hospital_name")
        self.patient_id = user_data.get("patient_id")
        self.lab_id = user_data.get("lab_id")
        

@login_manager.user_loader
def load_user(user_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT user_id, user_role FROM UserAccount WHERE user_id = %s",(user_id,))
    user = cursor.fetchone()
    if not user : 
        cursor.close()
        conn.close()
        return None 
    
    # If Admin fetch hospital_id and hospital_name
    if user["user_role"] in ("Admin") :
        cursor.execute("""
            SELECT 
                a.hospital_id,
                h.hospital_name
            FROM Admin a
            JOIN Hospital h
            ON a.hospital_id = h.hospital_id
            WHERE a.user_id = %s
        """, (user_id,))

        admin = cursor.fetchone()
        if admin:
            user["hospital_id"] = admin["hospital_id"]
            user["hospital_name"] = admin["hospital_name"]
       

    
    # If Patient fetch patient_id
    if user["user_role"] == "Patient":
        cursor.execute("""
            SELECT patient_id
            FROM Patient
            WHERE user_id = %s
        """, (user_id,))

        patient = cursor.fetchone()

        if patient:
            user["patient_id"] = patient["patient_id"]

    # If labstaff fetch lab_id + hospital
    if user["user_role"] == "LabStaff": 
        cursor.execute("""
            SELECT 
                ls.lab_id,
                l.hospital_id,
                h.hospital_name
            FROM LabStaff ls
            JOIN DiagnosticLab l ON ls.lab_id = l.lab_id
            JOIN Hospital h ON l.hospital_id = h.hospital_id
            WHERE ls.user_id = %s
        """, (user_id, ))

        labstaff = cursor.fetchone()

        if labstaff:
            user["lab_id"] = labstaff["lab_id"]
            user["hospital_id"] = labstaff["hospital_id"]
            user["hospital_name"] = labstaff["hospital_name"]


    # If doctor fetch hospital
    if user["user_role"] == "Doctor":
        cursor.execute("""
            SELECT 
                d.department_id,
                h.hospital_id,
                h.hospital_name
            FROM Doctor d
            JOIN Department dep ON d.department_id = dep.department_id
            JOIN Hospital h ON dep.hospital_id = h.hospital_id
            WHERE d.user_id = %s
        """, (user_id,))

        doctor = cursor.fetchone()

        if doctor:
            user["hospital_id"] = doctor["hospital_id"]
            user["hospital_name"] = doctor["hospital_name"]

    cursor.close()
    conn.close()
    return User(user)

def create_app() : 
    app = Flask(__name__)
    app.config.from_object(Config)
    
    bcrypt.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    from .routes.auth import auth_bp 
    from .routes.patient import patient_bp
    from .routes.doctor import doctor_bp
    from .routes.admin import admin_bp
    from .routes.labstaff import labstaff_bp
    from .routes.superadmin import superadmin_bp


    app.register_blueprint(auth_bp)
    app.register_blueprint(patient_bp)
    app.register_blueprint(doctor_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(labstaff_bp)
    app.register_blueprint(superadmin_bp)

    return app