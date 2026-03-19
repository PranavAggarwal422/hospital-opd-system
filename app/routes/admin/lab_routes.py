from flask import render_template, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from app.decorators.role_required import role_required
from app.forms.admin.lab_form import AddLabForm
from app.services.admin.lab_service import *
from app.routes.helpers import flash_form_errors
from mysql.connector import Error
from . import admin_bp


@admin_bp.route("/labs")
@login_required
@role_required("Admin")
def labs():
    hospital_id = current_user.hospital_id
    labs = get_labs_by_hospital(hospital_id)
    form = AddLabForm()
    return render_template("admin/labs.html", labs=labs, form=form)

@admin_bp.route("/labs/add", methods=["POST"])
@login_required
@role_required("Admin")
def add_lab():
    hospital_id = current_user.hospital_id
    form = AddLabForm()

    if form.validate_on_submit():
        data = {
            "hospital_id": hospital_id,
            "lab_name": form.lab_name.data.strip(),
            "location": form.location.data.strip() if form.location.data else None
        }
        try:
            create_lab(data)
            flash("Lab added successfully", "success")

        except ValueError as e:
            flash(str(e), "danger")

        except Error as e:
            flash(e.msg, "danger")
        
        except Exception:
            flash("Something went wrong","danger")
    
    if form.errors:
        flash_form_errors(form)

    return redirect(url_for("admin.labs"))

@admin_bp.route("/labs/deactivate/<int:lab_id>", methods=["POST"])
@login_required
@role_required("Admin")
def deactivate_lab(lab_id):
    lab = get_lab_by_hospital(lab_id, current_user.hospital_id)
    if not lab:
        abort(404)
    try:
        set_lab_status(lab_id, False)
        flash("Lab deactivated","success")
    except ValueError as e:
        flash(str(e), "danger")
    except Error as e:
        flash(e.msg,"danger")
    except Exception:
        flash("Something went wrong","danger")

    return redirect(url_for("admin.labs"))

@admin_bp.route("/labs/activate/<int:lab_id>", methods=["POST"])
@login_required
@role_required("Admin")
def activate_lab(lab_id):
    lab = get_lab_by_hospital(lab_id, current_user.hospital_id)
    if not lab:
        abort(404)
    try : 
        set_lab_status(lab_id, True)
        flash("Lab activated", "success")
    except ValueError as e:
        flash(str(e), "danger")
    except Error as e : 
        flash(e.msg, "danger")
    except Exception:
        flash("Something went wrong","danger")

    return redirect(url_for("admin.labs"))


