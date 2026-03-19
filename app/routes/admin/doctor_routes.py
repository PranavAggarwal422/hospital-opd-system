from flask import render_template, redirect, url_for, flash, abort, request
from flask_login import login_required, current_user
from app.decorators.role_required import role_required
from app.forms.admin.doctor_form import AddDoctorForm
from app.services.admin.doctor_service import *
from app.services.admin.department_service import get_department_by_hospital
from app.routes.helpers import flash_form_errors
from mysql.connector import Error
from . import admin_bp
from app import bcrypt 


@admin_bp.route("/departments/doctors/<int:department_id>")
@login_required
@role_required("Admin")
def department_doctors(department_id):
    hospital_id = current_user.hospital_id
    department = get_department_by_hospital(department_id, hospital_id)

    if not department:
        abort(404)

    doctors = get_doctors_by_department(department_id)
    form = AddDoctorForm()

    return render_template("admin/department_doctors.html", department=department, doctors=doctors,form=form)

@admin_bp.route("/departments/doctors/<int:department_id>/add", methods=["POST"])
@login_required
@role_required("Admin")
def add_doctor(department_id):
    hospital_id = current_user.hospital_id
    department = get_department_by_hospital(department_id, hospital_id)
    if not department:
        abort(404)
    if department["is_active"] == False:
        flash("Cannot add doctor to an inactive department","danger")
        return redirect(url_for("admin.departments"))

    form = AddDoctorForm()

    if form.validate_on_submit():
        password_hash = bcrypt.generate_password_hash(form.password.data).decode("utf-8")

        data = {
            "doctor_name": form.doctor_name.data.strip(),
            "gender": form.gender.data,
            "department_id": department_id,
            "email": form.email.data.strip() or None,
            "phone": form.phone.data.strip() or None,
            "password_hash": password_hash
        }

        try:
            create_doctor(data)
            flash("Doctor created successfully","success")

        except ValueError as e:
            flash(str(e),"danger")
        
        except Error as e:
            flash(e.msg,"danger")

        except Exception as e:
            flash("Something went wrong","danger")
    
    if form.errors:
        flash_form_errors(form)

    return redirect(url_for("admin.department_doctors", department_id=department_id))
    
@admin_bp.route("/departments/doctors/deactivate/<int:doctor_id>", methods=["POST"])
@login_required
@role_required("Admin")
def remove_doctor(doctor_id):
    doctor = get_doctor_by_hospital_id(doctor_id, current_user.hospital_id)
    if not doctor:
        abort(404)
    try:
        deactivate_doctor(doctor_id)
        flash("Doctor deactivated","success")

    except ValueError as e:
        flash(str(e), "danger")
    
    except Error as e:
        flash(e.msg,"danger")

    except Exception:
        flash("Something went wrong","danger")

    return redirect(request.referrer or url_for("admin.departments"))

