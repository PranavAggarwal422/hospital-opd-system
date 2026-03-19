from flask import redirect, url_for, flash
from flask_login import login_required
from mysql.connector import Error
from app.decorators.role_required import role_required
from app.services.superadmin.hospital_service import *
from app.forms.superadmin.hospital_form import AddHospitalForm
from app.routes.helpers import flash_form_errors
from . import superadmin_bp

@superadmin_bp.route("/hospitals/add", methods=["POST"])
@login_required
@role_required("SuperAdmin")
def add_hospital():
    form = AddHospitalForm()

    if form.validate_on_submit():
        data = {
            "hospital_name": form.hospital_name.data.strip(),
            "address": form.address.data.strip() or None,
            "city": form.city.data.strip(),
            "state": form.state.data.strip(),
            "pincode": form.pincode.data
        }

        try:
            create_hospital(data)
            flash(f"{data['hospital_name']} added successfully", "success")

        except ValueError as e:
            flash(str(e), "danger")
        
        except Error as e:
            flash(e.msg,"danger")

        except Exception:
            flash("Something went wrong", "danger")

        return redirect(url_for("superadmin.dashboard"))

    if form.errors:
        flash_form_errors(form)
        return redirect(url_for("superadmin.dashboard"))


@superadmin_bp.route("/hospitals/deactivate/<int:hospital_id>", methods = ["POST"])
@login_required
@role_required("SuperAdmin")
def deactivate(hospital_id):
    try : 
        deactivate_hospital(hospital_id)
        flash("Hospital deactivated", "success")
    except Error as e:
            flash(e.msg,"danger")
    except Exception : 
        flash("Something went wrong", "danger")

    return redirect(url_for("superadmin.dashboard"))


@superadmin_bp.route("/hospitals/activate/<int:hospital_id>", methods = ["POST"])
@login_required
@role_required("SuperAdmin")
def activate(hospital_id):
    try : 
        activate_hospital(hospital_id)
        flash("Hospital activated", "success")
    except Error as e:
            flash(e.msg,"danger")
    except Exception : 
        flash("Something went wrong", "danger")

    return redirect(url_for("superadmin.dashboard"))

