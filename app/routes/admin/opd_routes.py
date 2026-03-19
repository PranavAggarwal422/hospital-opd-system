from flask import render_template, redirect, url_for, flash, abort, request
from flask_login import login_required, current_user
from app.decorators.role_required import role_required
from app.forms.admin.opd_form import AddOPDForm
from app.services.admin.opd_service import *
from app.services.admin.department_service import get_department_by_hospital
from app.routes.helpers import flash_form_errors
from mysql.connector import Error
from . import admin_bp
from app import bcrypt 

# View OPD rooms of a department
@admin_bp.route("/departments/opd/<int:department_id>")
@login_required
@role_required("Admin")
def department_opd(department_id):
    hospital_id = current_user.hospital_id
    department = get_department_by_hospital(department_id, hospital_id)

    if not department:
        abort(404)

    opd_rooms = get_opd_by_department(department_id)
    form = AddOPDForm()

    return render_template("admin/department_opd.html", department=department, opd_rooms=opd_rooms,form=form)

# Add OPD room
@admin_bp.route("/departments/opd/<int:department_id>/add", methods=["POST"])
@login_required
@role_required("Admin")
def add_opd(department_id):
    hospital_id = current_user.hospital_id
    department = get_department_by_hospital(department_id, hospital_id)
    if not department:
        abort(404)
    if department["is_active"] == False:
        flash("Cannot add OPD room to an inactive department","danger")
        return redirect(url_for("admin.departments"))
        
    form = AddOPDForm()

    if form.validate_on_submit():
        data = {
            "room_no": form.room_no.data.strip(),
            "department_id": department_id,
            "hospital_id": hospital_id
        }

        try:
            create_opd(data)
            flash("OPD room added successfully", "success")
        except ValueError as e:
            flash(str(e), "danger")
        
        except Error as e:
            flash(e.msg,"danger")

        except Exception:
            flash("Something went wrong", "danger")

    if form.errors:
        flash_form_errors(form)

    return redirect(url_for("admin.department_opd", department_id=department_id))

# Deactivate OPD
@admin_bp.route("/departments/opd/deactivate/<int:opd_id>", methods=["POST"])
@login_required
@role_required("Admin")
def deactivate_opd_route(opd_id):
    opd = get_opd_by_hospital_id(opd_id, current_user.hospital_id)
    if not opd:
        abort(404)

    try:
        deactivate_opd(opd_id)
        flash("OPD room deactivated", "success")
    
    except ValueError as e:
        flash(str(e), "danger")
    
    except Error as e:
        flash(e.msg,"danger")

    except Exception:
        flash("Something went wrong", "danger")

    return redirect(request.referrer or url_for("admin.departments"))

# Activate OPD
@admin_bp.route("/departments/opd/activate/<int:opd_id>", methods=["POST"])
@login_required
@role_required("Admin")
def activate_opd_route(opd_id):
    opd = get_opd_by_hospital_id(opd_id, current_user.hospital_id)
    if not opd:
        abort(404)
        
    try:
        activate_opd(opd_id)
        flash("OPD room activated", "success")
    
    except ValueError as e:
        flash(str(e), "danger")

    except Error as e:
            flash(e.msg,"danger")

    except Exception:
        flash("Something went wrong", "danger")

    return redirect(request.referrer or url_for("admin.departments"))

    
