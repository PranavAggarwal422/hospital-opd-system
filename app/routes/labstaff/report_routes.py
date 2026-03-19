from flask import render_template, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from app.decorators.role_required import role_required
from app.forms.labstaff.test_forms import UploadReportForm
from app.services.labstaff.report_service import *
from app.services.labstaff.test_request_service import get_test_request_by_id
from app.routes.helpers import flash_form_errors
from . import labstaff_bp

@labstaff_bp.route("/tests/<int:request_id>/upload", methods=["GET", "POST"])
@login_required
@role_required("LabStaff")
def upload_report_route(request_id):
    lab_id = current_user.lab_id
    request_data = get_test_request_by_id(request_id, lab_id)
    if not request_data:
        abort(404)

    form = UploadReportForm()

    if form.validate_on_submit():
        try:
            file = form.report_url.data
            filename = save_report_file(file)
            data = {
                "request_id": request_id,
                "report_url": filename,
                "remarks": form.remarks.data
            }

            upload_report(data)
            flash("Report uploaded successfully", "success")
            return redirect(url_for("labstaff.test_requests"))

        except ValueError as e:
            flash(str(e), "danger")

        except Exception:
            flash("Something went wrong", "danger")
        return redirect(url_for("labstaff.upload_report_route", request_id=request_id))

    if form.errors:
        flash_form_errors(form)
        return redirect(url_for("labstaff.upload_report_route", request_id=request_id))

    return render_template("lab/upload_report.html", form=form, request_data =request_data)

