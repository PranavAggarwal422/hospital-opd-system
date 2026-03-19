from flask import render_template
from flask_login import login_required
from app.decorators.role_required import role_required
from app.services.superadmin.hospital_service import get_all_hospitals
from app.forms.superadmin.hospital_form import AddHospitalForm
from . import superadmin_bp

@superadmin_bp.route("/dashboard")
@login_required
@role_required("SuperAdmin")
def dashboard():
    form = AddHospitalForm()
    hospitals = get_all_hospitals()
    return render_template("superadmin/dashboard.html",hospitals=hospitals, form = form)
