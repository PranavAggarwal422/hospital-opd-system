from flask import render_template, redirect, url_for, flash, abort, request
from flask_login import login_required, current_user
from app.decorators.role_required import role_required
from app.forms.admin.test_form import AddHospitalTestForm
from app.forms.empty_form import EmptyForm
from app.services.admin.test_service import *
from app.services.admin.lab_service import get_lab_by_hospital
from app.routes.helpers import flash_form_errors

from mysql.connector import Error
from . import admin_bp


@admin_bp.route("/tests")
@login_required
@role_required("Admin")
def hospital_tests():
    hospital_id = current_user.hospital_id
    tests = get_tests_by_hospital(hospital_id)
    form = AddHospitalTestForm()

    return render_template("admin/tests.html", tests=tests, form=form)

@admin_bp.route("/tests/add", methods=["POST"])
@login_required
@role_required("Admin")
def add_test():
    hospital_id = current_user.hospital_id
    form = AddHospitalTestForm()

    if form.validate_on_submit():
        data = {
            "hospital_id": hospital_id,
            "test_type": form.test_type.data,
            "test_name": form.test_name.data.strip(),
            "test_description": form.test_description.data.strip() or None
        }

        try:
            create_hospital_test(data)
            flash("Test added successfully", "success")

        except ValueError as e:
            flash(str(e), "danger")

        except Error as e:
            flash(e.msg, "danger")
        
        except Exception:
            flash("Something went wrong","danger")

    if form.errors:
        flash_form_errors(form)

    return redirect(url_for("admin.hospital_tests"))


@admin_bp.route("/tests/deactivate/<int:test_id>", methods=["POST"])
@login_required
@role_required("Admin")
def deactivate_test(test_id):
    test = get_test_by_hospital(test_id, current_user.hospital_id)
    if not test:
        abort(404)
    try : 
        set_hospital_test_status(test_id, False)
        flash("Test disabled", "success")
    except ValueError as e:
        flash(str(e), "danger")
    except Error as e : 
        flash(e.msg, "danger")
    except Exception : 
        flash("Something went wrong", "danger")

    return redirect(url_for("admin.hospital_tests"))

@admin_bp.route("/tests/activate/<int:test_id>", methods=["POST"])
@login_required
@role_required("Admin")
def activate_test(test_id):
    test = get_test_by_hospital(test_id, current_user.hospital_id)
    if not test:
        abort(404)
    
    try : 
        set_hospital_test_status(test_id, True)
        flash("Test enabled", "success")
    except ValueError as e:
        flash(str(e), "danger")
    except Error as e : 
        flash(e.msg, "danger")
    except Exception : 
        flash("Something went wrong", "danger")

    return redirect(url_for("admin.hospital_tests"))


@admin_bp.route("/labs/<int:lab_id>/tests")
@login_required
@role_required("Admin")
def lab_tests(lab_id):
    hospital_id = current_user.hospital_id
    lab = get_lab_by_hospital(lab_id, hospital_id)
    if not lab:
        abort(404)

    available_tests = get_available_tests_for_lab(lab_id, hospital_id)
    assigned_tests = get_tests_by_lab(lab_id)
    form = EmptyForm() 

    return render_template("admin/lab_tests.html", lab=lab, available_tests=available_tests,assigned_tests=assigned_tests, form = form)


@admin_bp.route("/labs/<int:lab_id>/tests/add/<int:test_id>", methods=["POST"])
@login_required
@role_required("Admin")
def assign_test(lab_id, test_id):
    lab = get_lab_by_hospital(lab_id, current_user.hospital_id)
    if not lab:
        abort(404)
    if not lab["is_active"]:
        flash("Cannot assign test to inactive lab", "danger")
        return redirect(url_for("admin.labs"))
    
    test = get_test_by_hospital(test_id, current_user.hospital_id)
    if not test:
        abort(404)
    if not test["is_available"]:
        flash("Cannot assign an unavailable test to lab", "danger")
        return redirect(url_for("admin.hospital_tests"))
    
    try:
        assign_test_to_lab({"lab_id": lab_id, "test_id": test_id})
        flash("Test assigned to lab", "success")

    except ValueError as e:
        flash(str(e), "danger")
    except Error as e:
            flash(e.msg, "danger")
    except Exception:
        flash("Something went wrong","danger")

    return redirect(request.referrer or url_for("admin.lab_tests", lab_id=lab_id))

@admin_bp.route("/labs/<int:lab_id>/tests/deactivate/<int:test_id>", methods=["POST"])
@login_required
@role_required("Admin")
def disable_test(lab_id, test_id):
    lab = get_lab_by_hospital(lab_id, current_user.hospital_id)
    if not lab:
        abort(404)
    try:
        change_status_of_test_for_lab(lab_id, test_id, False)
        flash("Test disabled for this lab", "success")

    except ValueError as e:
        flash(str(e), "danger")
    except Exception:
        flash("Something went wrong", "danger")

    return redirect(request.referrer or url_for("admin.lab_tests", lab_id=lab_id))

@admin_bp.route("/labs/<int:lab_id>/tests/activate/<int:test_id>", methods=["POST"])
@login_required
@role_required("Admin")
def enable_test(lab_id, test_id):
    lab = get_lab_by_hospital(lab_id, current_user.hospital_id)
    if not lab:
        abort(404)

    try:
        change_status_of_test_for_lab(lab_id, test_id, True)
        flash("Test enabled for this lab", "success")

    except ValueError as e:
        flash(str(e), "danger")
    except Exception:
        flash("Something went wrong", "danger")

    return redirect(request.referrer or url_for("admin.lab_tests", lab_id=lab_id))
