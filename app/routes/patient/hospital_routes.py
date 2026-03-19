from flask import render_template, flash, request
from flask_login import login_required
from app.decorators.role_required import role_required
from app.services.patient.hospital_service import *
from . import patient_bp

@patient_bp.route("/hospitals")
@login_required
@role_required("Patient")
def hospitals():
    search = request.args.get("search", "").strip()
    try:
        hospitals = get_active_hospitals(search=search)
    except Exception as e:
        flash("Something went wrong while fetching hospitals.", "danger")
        hospitals = []

    return render_template("patient/hospitals.html", hospitals=hospitals)

@patient_bp.route("/hospital/<int:hospital_id>/departments")
@login_required
@role_required("Patient")
def hospital_departments(hospital_id):
    search = request.args.get("search", "").strip()
    try:
        departments = get_departments_by_hospital(hospital_id, search=search)
    except Exception as e:
        flash("Something went wrong while fetching departments.", "danger")
        departments = []

    return render_template("patient/departments.html", departments=departments)