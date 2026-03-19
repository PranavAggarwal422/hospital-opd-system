from flask import render_template, redirect, url_for, flash, abort, request
from flask_login import login_required, current_user
from app.decorators.role_required import role_required
from app.forms.admin.labstaff_form import AddLabStaffForm
from app.services.admin.labstaff_service import *
from app.services.admin.lab_service import get_lab_by_hospital
from app.routes.helpers import flash_form_errors
from mysql.connector import Error
from app import bcrypt 
from . import admin_bp


@admin_bp.route("/labs/<int:lab_id>/staff")
@login_required
@role_required("Admin")
def lab_staff(lab_id):
    hospital_id = current_user.hospital_id
    lab = get_lab_by_hospital(lab_id, hospital_id)
    if not lab:
        abort(404)

    staff = get_staffs_by_lab(lab_id)
    form = AddLabStaffForm()

    return render_template("admin/lab_staff.html", lab=lab, staff=staff, form=form)

@admin_bp.route("/labs/<int:lab_id>/staff/add", methods=["POST"])
@login_required
@role_required("Admin")
def add_lab_staff(lab_id):
    lab = get_lab_by_hospital(lab_id, current_user.hospital_id)
    if not lab:
        abort(404)
    if lab["is_active"] == False:
        flash("Cannot add staff to an inactive lab","danger")
        return redirect(url_for("admin.labs"))

    form = AddLabStaffForm()
    if form.validate_on_submit():
        password_hash = bcrypt.generate_password_hash(form.password.data).decode("utf-8")

        data = {
            "lab_id": lab_id,
            "staff_name": form.staff_name.data.strip(),
            "staff_role": form.staff_role.data,
            "email": form.email.data.strip() or None,
            "phone": form.phone.data.strip() or None,
            "password_hash": password_hash
        }

        try:
            create_lab_staff(data)
            flash("Lab staff added successfully", "success")

        except ValueError as e:
            flash(str(e), "danger")

        except Error as e:
            flash(e.msg, "danger")

        except Exception:
            flash("Something went wrong","danger")
    
    if form.errors:
        flash_form_errors(form)

    return redirect(request.referrer or url_for("admin.lab_staff", lab_id=lab_id))


@admin_bp.route("/labs/<int:lab_id>/staff/deactivate/<int:staff_id>", methods=["POST"])
@login_required
@role_required("Admin")
def deactivate_lab_staff_route(lab_id, staff_id):
    hospital_id = current_user.hospital_id
    lab = get_lab_by_hospital(lab_id, hospital_id)
    if not lab:
        abort(404)
    staff = get_staff_by_lab_id(staff_id, lab_id)
    if not staff:
        abort(404)

    try:
        deactivate_staff(staff_id)
        flash("Lab staff deactivated", "success")
    except ValueError as e:
        flash(str(e), "danger")

    except Error as e:
        flash(e.msg, "danger")

    except Exception:
        flash("Something went wrong", "danger")

    return redirect(request.referrer or url_for("admin.lab_staff", lab_id=lab_id))

