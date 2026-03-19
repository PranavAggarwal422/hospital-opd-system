from flask import render_template, redirect, url_for, flash, abort, request 
from flask_login import login_required
from app import bcrypt 
from mysql.connector import Error
from app.decorators.role_required import role_required
from app.services.superadmin.admin_service import *
from app.services.superadmin.hospital_service import get_hospital
from app.forms.superadmin.admin_form import AddAdminForm
from app.routes.helpers import flash_form_errors
from .import superadmin_bp 

@superadmin_bp.route("/hospitals/admins/<int:hospital_id>")
@login_required
@role_required("SuperAdmin")
def hospital_admins(hospital_id):
    hospital = get_hospital(hospital_id)
    if(not hospital) : 
        abort(404, "Hospital not found")

    admins = get_admins_by_hospital(hospital_id)

    add_admin_form = AddAdminForm()

    return render_template("superadmin/hospital_admins.html", hospital=hospital, admins=admins,add_admin_form= add_admin_form)


@superadmin_bp.route("/hospitals/admins/<int:hospital_id>/add", methods=["POST"])
@login_required
@role_required("SuperAdmin")

def add_admin(hospital_id):
    hospital = get_hospital(hospital_id)
    if not hospital : 
        abort(404)
    if not hospital["is_active"]:
        flash("Cannot add admin to inactive hospital", "danger")
        return redirect(url_for("superadmin.dashboard"))
        
    form = AddAdminForm()
    if form.validate_on_submit():
        password_hash = bcrypt.generate_password_hash(form.password.data).decode("utf-8")

        data = {
            "admin_name": form.admin_name.data.strip(),
            "email": form.email.data.strip() or None,
            "phone": form.phone.data.strip() or None,
            "password_hash": password_hash,
            "hospital_id": hospital_id
        }

        try:
            create_admin(data)
            flash("Admin created successfully", "success")

        except ValueError as e:
            flash(str(e), "danger")
        except Error as e:
            flash(e.msg,"danger")
        except Exception:
            flash("Something went wrong", "danger")
        
    if form.errors:
        flash_form_errors(form)
        return redirect(url_for("superadmin.hospital_admins",hospital_id=hospital_id))

    return redirect(url_for("superadmin.hospital_admins", hospital_id=hospital_id))



@superadmin_bp.route("/hospitals/admins/remove/<int:admin_id>", methods=["POST"])
@login_required
@role_required("SuperAdmin")
def remove_admin(admin_id):
    try:
        deactivate_admin(admin_id)
        flash("Admin removed", "success")
    except Error as e:
        flash(e.msg,"danger")
    except Exception:
        flash("Something went wrong", "danger")

    return redirect(request.referrer or url_for("superadmin.dashboard"))

