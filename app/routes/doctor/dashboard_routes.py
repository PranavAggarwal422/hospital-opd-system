from flask import render_template
from flask_login import login_required, current_user
from app.decorators.role_required import role_required
from app.services.doctor.schedule_service import *
from .import doctor_bp

@doctor_bp.route("/dashboard")
@login_required
@role_required("Doctor")
def dashboard():
    sessions = get_doctor_schedule(current_user.id)
    return render_template("doctor/dashboard.html", sessions=sessions)
