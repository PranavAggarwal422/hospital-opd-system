from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.decorators.role_required import role_required
from app.forms.profile_form import EditProfileForm
from app.services.admin.admin_profile_service import *
from app.routes.helpers import flash_form_errors
from mysql.connector import Error
from . import admin_bp


@admin_bp.route("/profile")
@login_required
@role_required("Admin")
def profile():
    hospital_id = current_user.hospital_id
    user_id = current_user.id
    admin = get_admin_by_user(user_id)
    hospital = get_hospital_by_id(hospital_id)

    return render_template("admin/profile.html", admin=admin, hospital=hospital)

@admin_bp.route("/profile/edit", methods=["GET","POST"])
@login_required
@role_required("Admin")
def edit_profile():
    form = EditProfileForm()
    admin = get_admin_by_user(current_user.id)

    if form.validate_on_submit():
        phone = form.phone.data or None
        name = form.name.data 
        try : 
            update_admin_profile(current_user.id,name,phone)
            flash("Profile updated successfully","success")
            return redirect(url_for("admin.profile"))
        except ValueError as e:
            flash(str(e), "danger")
        
        except Error as e:
            flash(e.msg,"danger")

        except Exception:
            flash("Something went wrong", "danger")
        return redirect(url_for("admin.edit_profile"))

    if form.errors:
        flash_form_errors(form)
        return redirect(url_for("admin.edit_profile"))
        
        
    if request.method == "GET":
        form.name.data = admin["admin_name"]
        form.phone.data = admin["phone"]

    return render_template("admin/edit_profile.html", form=form)

