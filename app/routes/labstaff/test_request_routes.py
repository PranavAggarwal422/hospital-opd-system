from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from mysql.connector import Error

from app.decorators.role_required import role_required
from app.forms.labstaff.test_forms import CreateTestRequestForm
from app.services.labstaff.test_request_service import *
from app.routes.helpers import flash_form_errors
from . import labstaff_bp

@labstaff_bp.route("/tests")
@login_required
@role_required("LabStaff")
def test_requests():
    lab_id = current_user.lab_id
    tests = get_lab_test_requests(lab_id)
    return render_template("lab/test_requests.html",tests=tests)


@labstaff_bp.route("/tests/create", methods=["GET","POST"])
@login_required
@role_required("LabStaff")
def create_test_request_route():
    lab_id = current_user.lab_id
    form = CreateTestRequestForm()
    form.test_id.choices = get_tests_supported_by_lab(lab_id)
    form.department_id.choices = get_departments_of_lab_hospital(lab_id)

    if form.validate_on_submit():
        data = {
            "email_or_phone": form.email_or_phone.data,
            "department_id": form.department_id.data,
            "appointment_date": form.appointment_date.data,
            "test_id": form.test_id.data,
            "lab_id": lab_id
        }

        try:
            create_test_request(data)
            flash("Test request created successfully","success")
            return redirect(url_for("labstaff.test_requests"))

        except ValueError as e:
            flash(str(e),"danger")

        except Error as e:
            flash(e.msg,"danger")

        except Exception:
            flash("Something went wrong","danger")
        
        return redirect(url_for("labstaff.create_test_request_route"))

    if form.errors:
        flash_form_errors(form)
        return redirect(url_for("labstaff.create_test_request_route"))

    return render_template("lab/create_test_request.html", form=form)


@labstaff_bp.route("/tests/<int:request_id>/collect", methods=["POST"])
@login_required
@role_required("LabStaff")
def collect_sample_route(request_id):
    lab_id = current_user.lab_id

    try:
        collect_sample(request_id, lab_id)
        flash("Sample collected successfully", "success")

    except ValueError as e:
        flash(str(e), "danger")

    except Error as e:
        flash(e.msg, "danger")

    except Exception:
        flash("Something went wrong", "danger")

    return redirect(request.referrer or url_for("labstaff.test_requests"))

