from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from mysql.connector import Error
from app.decorators.role_required import role_required
from app.services.labstaff.labstaff_profile_service import *
from app.routes.helpers import flash_form_errors
from app.forms.profile_form import EditProfileForm
from . import labstaff_bp


@labstaff_bp.route("/profile")
@login_required
@role_required("LabStaff")
def profile():
    user_id = current_user.id
    lab_id = current_user.lab_id
    hospital_id = current_user.hospital_id

    staff = get_labstaff_by_user(user_id)
    lab = get_lab_by_id(lab_id)
    hospital = get_hospital_by_id(hospital_id)

    return render_template("lab/profile.html", staff=staff, lab=lab, hospital = hospital)


@labstaff_bp.route("/profile/edit", methods=["GET", "POST"])
@login_required
@role_required("LabStaff")
def edit_profile():
    form = EditProfileForm()
    staff = get_labstaff_by_user(current_user.id)

    if form.validate_on_submit():
        phone = form.phone.data or None
        name = form.name.data
        try:
            update_labstaff_profile(current_user.id,name,phone)
            flash("Profile updated successfully", "success")
            return redirect(url_for("labstaff.profile"))

        except ValueError as e:
            flash(str(e), "danger")

        except Error as e:
            flash(e.msg, "danger")

        except Exception:
            flash("Something went wrong", "danger")
        return redirect(url_for("labstaff.edit_profile"))

    if form.errors:
        flash_form_errors(form)
        return redirect(url_for("labstaff.edit_profile"))

    if request.method == "GET":
        form.name.data = staff["staff_name"]
        form.phone.data = staff["phone"]

    return render_template("lab/edit_profile.html", form=form)
