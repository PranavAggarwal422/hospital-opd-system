from flask import render_template, flash, redirect, url_for, request
from flask_login import login_required, current_user
from app.decorators.role_required import role_required
from app.services.doctor.doctor_profile_service import *
from app.forms.profile_form import EditProfileForm
from app.routes.helpers import flash_form_errors
from mysql.connector import Error
from . import doctor_bp

@doctor_bp.route("/profile")
@login_required
@role_required("Doctor")
def profile():
    user_id = current_user.id
    hospital_id = current_user.hospital_id
    doctor = get_doctor_by_user(user_id)
    hospital = get_hospital_by_id(hospital_id)

    return render_template("doctor/profile.html", doctor=doctor, hospital=hospital)


@doctor_bp.route("/profile/edit", methods=["GET", "POST"])
@login_required
@role_required("Doctor")
def edit_profile():
    form = EditProfileForm()
    doctor = get_doctor_by_user(current_user.id)

    if form.validate_on_submit():
        phone = form.phone.data or None
        name = form.name.data
        try:
            update_doctor_profile(current_user.id, name, phone)
            flash("Profile updated successfully", "success")
            return redirect(url_for("doctor.profile"))

        except ValueError as e:
            flash(str(e), "danger")
        except Error as e : 
            flash(e.msg, "danger")
        except Exception:
            flash("Something went wrong", "danger")
        return redirect(url_for("doctor.edit_profile"))

    if form.errors:
        flash_form_errors(form)
        return redirect(url_for("doctor.edit_profile"))

    if request.method == "GET":
        form.name.data = doctor["doctor_name"]
        form.phone.data = doctor["phone"]

    return render_template("doctor/edit_profile.html", form=form)

