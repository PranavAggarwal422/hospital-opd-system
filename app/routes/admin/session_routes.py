from flask import render_template, redirect, url_for, flash, abort, request
from flask_login import login_required, current_user
from app.decorators.role_required import role_required
from app.forms.admin.opd_form import AddSessionForm
from app.services.admin.session_service import *
from app.services.admin.opd_service import get_opd_by_hospital_id
from app.routes.helpers import flash_form_errors
from mysql.connector import Error
from . import admin_bp


# View sessions of an OPD room
@admin_bp.route("/opd/sessions/<int:opd_id>")
@login_required
@role_required("Admin")
def opd_sessions(opd_id):
    hospital_id = current_user.hospital_id  
    opd = get_opd_by_hospital_id(opd_id, hospital_id)
    if not opd:
        abort(404)

    sessions = get_sessions_by_opd(opd_id)
    form = AddSessionForm()

    return render_template("admin/opd_sessions.html", sessions=sessions, opd_id=opd_id, department_id=opd["department_id"],form=form)

# Add session to an OPD room
@admin_bp.route("/opd/sessions/<int:opd_id>/add", methods=["POST"])
@login_required
@role_required("Admin")
def add_session(opd_id):
    hospital_id = current_user.hospital_id  
    opd = get_opd_by_hospital_id(opd_id, hospital_id)
    if not opd:
        abort(404)
    if not opd["is_active"]:
        flash("Cannot add session to an inactive OPD room","danger")
        return redirect(url_for("admin.opd_sessions", opd_id=opd_id))

    form = AddSessionForm()
    if form.validate_on_submit():
        data = {
            "opd_id": opd_id,
            "week_day": form.week_day.data,
            "start_time": form.start_time.data,
            "end_time": form.end_time.data,
            "max_tokens": form.max_tokens.data,
            "email_or_phone": form.email_or_phone.data.strip() or None,
            "is_email": form.is_email
        }

        try:
            create_session(data)
            flash("Session created successfully","success")

        except ValueError as e:
            flash(str(e),"danger")
        
        except Error as e:
            flash(e.msg,"danger")

        except Exception:
            flash("Something went wrong","danger")
        
    if form.errors:
        flash_form_errors(form)

    return redirect(url_for("admin.opd_sessions", opd_id=opd_id))

# Deactivate session
@admin_bp.route("/opd/sessions/deactivate/<int:session_id>", methods=["POST"])
@login_required
@role_required("Admin")
def deactivate_session_route(session_id):
    opd_session = get_session_by_hospital_id(session_id, current_user.hospital_id)
    if not opd_session:
        abort(404)
    try:
        deactivate_session(session_id)
        flash("Session deactivated","success")
    
    except ValueError as e:
        flash(str(e), "danger")
    
    except Error as e:
        flash(e.msg,"danger")

    except Exception:
        flash("Something went wrong","danger")

    return redirect(request.referrer or url_for("admin.departments"))

# Activate session
@admin_bp.route("/opd/sessions/activate/<int:session_id>", methods=["POST"])
@login_required
@role_required("Admin")
def activate_session_route(session_id):
    session = get_session_by_hospital_id(session_id, current_user.hospital_id)
    if not session:
        abort(404)
    try:
        activate_session(session_id)
        flash("Session activated","success")
    
    except ValueError as e:
        flash(str(e), "danger")
    
    except Error as e:
        flash(e.msg,"danger")

    except Exception:
        flash("Something went wrong","danger")

    return redirect(request.referrer or url_for("admin.departments"))

