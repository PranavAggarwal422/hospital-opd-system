from flask import render_template, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from app.decorators.role_required import role_required
from app.forms.admin.department_form import AddDepartmentForm
from app.services.admin.department_service import *
from app.routes.helpers import flash_form_errors
from mysql.connector import Error
from . import admin_bp

@admin_bp.route("/departments")
@login_required
@role_required("Admin")
def departments():
    hospital_id = current_user.hospital_id
    form = AddDepartmentForm()
    departments = get_departments_by_hospital(hospital_id)
    return render_template("admin/departments.html", departments=departments, form=form)

@admin_bp.route("/departments/add", methods=["POST"])
@login_required
@role_required("Admin")
def add_department():
    hospital_id = current_user.hospital_id
    form = AddDepartmentForm()

    if form.validate_on_submit():
        data = {
            "department_name": form.department_name.data.strip(),
            "hospital_id": hospital_id
        }
        try:
            create_department(data)
            flash("Department added successfully", "success")

        except ValueError as e:
            flash(str(e), "danger")
        
        except Error as e:
            flash(e.msg,"danger")

        except Exception:
            flash("Something went wrong", "danger")

    if form.errors:
        flash_form_errors(form)

    return redirect(url_for("admin.departments"))

@admin_bp.route("/departments/deactivate/<int:department_id>", methods=["POST"])
@login_required
@role_required("Admin")
def deactivate_department_route(department_id):
    hospital_id = current_user.hospital_id
    department = get_department_by_hospital(department_id, hospital_id)
    if not department:
        abort(404)

    try:
        deactivate_department(department_id)
        flash("Department deactivated", "success")
    
    except ValueError as e:
        flash(str(e), "danger")
    
    except Error as e:
            flash(e.msg,"danger")

    except Exception:
        flash("Something went wrong", "danger")

    return redirect(url_for("admin.departments"))

@admin_bp.route("/departments/activate/<int:department_id>", methods=["POST"])
@login_required
@role_required("Admin")
def activate_department_route(department_id):
    hospital_id = current_user.hospital_id
    department = get_department_by_hospital(department_id, hospital_id)
    if not department:
        abort(404)
    try:
        activate_department(department_id)
        flash("Department activated", "success")
    except ValueError as e:
        flash(str(e), "danger")
    
    except Error as e:
            flash(e.msg,"danger")

    except Exception:
        flash("Something went wrong", "danger")

    return redirect(url_for("admin.departments"))

