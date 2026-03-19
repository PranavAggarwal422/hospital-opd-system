from flask import render_template
from flask_login import login_required, current_user
from app.decorators.role_required import role_required
from app.services.patient.appointment_service import get_upcoming_appointments
from app.services.patient.report_service import get_recent_reports 
from . import patient_bp


@patient_bp.route("/dashboard")
@login_required
@role_required("Patient")
def dashboard():
    patient_id = current_user.patient_id
    appointments = get_upcoming_appointments(patient_id)
    reports = get_recent_reports(patient_id)

    return render_template("patient/dashboard.html", appointments=appointments, reports=reports)
