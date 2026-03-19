from flask import render_template, abort, send_from_directory, flash, request, current_app
from flask_login import login_required, current_user
from app.decorators.role_required import role_required
from app.services.patient.report_service import *
from . import patient_bp
import os 


@patient_bp.route("/reports")
@login_required
@role_required("Patient")
def reports():
    patient_id = current_user.patient_id
    search = request.args.get("search", "").strip()
    try:
        reports = get_all_reports(patient_id, search=search)
    except Exception as e:
        flash("Something went wrong while fetching reports.", "danger")
        reports = []

    return render_template("patient/reports.html",reports=reports)


@patient_bp.route("/reports/<int:request_id>")
@login_required
@role_required("Patient")
def download_report(request_id):
    report = get_report_by_request(request_id, current_user.patient_id)
    if not report:
        abort(404)

    upload_folder = current_app.config["UPLOAD_FOLDER"]
    filepath = os.path.join(upload_folder, report["report_url"])
    if not os.path.exists(filepath):
        abort(404)

    return send_from_directory(upload_folder, report["report_url"], as_attachment=True)

