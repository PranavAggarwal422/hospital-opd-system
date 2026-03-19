from flask import render_template, abort, flash, redirect ,url_for
from flask_login import login_required, current_user
from app.decorators.role_required import role_required
from app.services.patient.patient_profile_service import *
from app.forms.patient.patient_profile_form import EditProfileForm
from app.routes.helpers import flash_form_errors
from mysql.connector import Error
from . import patient_bp

@patient_bp.route("/profile")
@login_required
@role_required("Patient")
def profile():
    patient = get_patient_by_id(current_user.patient_id)
    return render_template("patient/profile.html", patient=patient)

@patient_bp.route("/profile/edit", methods=["GET", "POST"])
@login_required
@role_required("Patient")
def edit_profile():
    patient = get_patient_by_id(current_user.patient_id)
    if not patient:
        abort(404)

    form = EditProfileForm(data=patient)
    if form.validate_on_submit():
        data = {
            "patient_name": form.patient_name.data,
            "email": form.email.data.strip() or None,
            "phone": form.phone.data.strip() or None,
            "dob": form.dob.data or None,
            "gender": form.gender.data,
            "address": form.address.data.strip() or None
        }

        try:
            update_patient_profile(current_user.patient_id, data)
            flash("Profile updated successfully", "success")
            return redirect(url_for("patient.profile"))
        except ValueError as e:
            flash(str(e), "danger")
        except Error as e:
            flash(e.msg,"danger")
        except Exception:
            flash("Something went wrong", "danger")
        return redirect(url_for("patient.edit_profile"))
    
    if form.errors:
        flash_form_errors(form)
        return redirect(url_for("patient.edit_profile"))

    return render_template("patient/edit_profile.html", form=form)


