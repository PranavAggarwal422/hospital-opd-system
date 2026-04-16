from flask import render_template, abort, flash, redirect ,url_for, request
from flask_login import login_required, current_user
from app.decorators.role_required import role_required
from app.services.patient.appointment_service import *
from app.forms.patient.appointment_form import BookAppointmentForm
from app.routes.helpers import flash_form_errors
from mysql.connector import Error
from collections import defaultdict
from . import patient_bp

@patient_bp.route("/departments/<int:department_id>/sessions")
@login_required
@role_required("Patient")
def department_sessions(department_id):
    search = request.args.get("search", "").strip()
    try:
        sessions = get_sessions_by_department(department_id, search=search)
    except Exception as e:
        flash("Something went wrong while fetching sessions.", "danger")
        sessions = []

    # GROUP BY DOCTOR_ID
    doctors = defaultdict(list)
    for s in sessions:
        doctors[s["doctor_id"]].append(s)

    form = BookAppointmentForm()
    return render_template("patient/opd_sessions.html", doctors=doctors, form=form)


@patient_bp.route("/sessions/book", methods=["POST"])
@login_required
@role_required("Patient")
def book_appointment_route():
    session_id = request.form.get("session_id")
    if not session_id:
        flash("Please select a session.", "danger")
        return redirect(request.referrer or url_for("patient.dashboard"))
    
    try:
        session_id = int(session_id)
    except ValueError:
        flash("Invalid session selected.", "danger")
        return redirect(request.referrer or url_for("patient.dashboard"))
    
    form = BookAppointmentForm()

    if form.validate_on_submit():
        data = {
            "patient_id": current_user.patient_id,
            "session_id": session_id,
            "appointment_date": form.appointment_date.data
        }

        try:
            book_appointment(data)
            flash("Appointment booked successfully", "success")

        except ValueError as e:
            flash(str(e), "danger")

        except Error as e:
            if "Session token limit reached" in str(e):
                flash("This session is fully booked. Please choose another date or session.", "danger")
            else:
                flash(e.msg, "danger")

        except Exception:
            flash("Something went wrong", "danger")

    if form.errors:
        flash_form_errors(form)

    return redirect(request.referrer or url_for("patient.dashboard"))


@patient_bp.route("/appointments")
@login_required
@role_required("Patient")
def appointment_history():
    patient_id = current_user.patient_id
    search = request.args.get("search", "").strip()

    try:
        appointments = get_patient_appointments(patient_id, search=search)
    except Exception as e:
        flash("Something went wrong while fetching appointments.", "danger")
        appointments = []

    return render_template("patient/appointment_history.html", appointments=appointments)

@patient_bp.route("/appointments/<int:appointment_id>/cancel", methods=["POST"])
@login_required
@role_required("Patient")
def cancel_appointment_route(appointment_id):
    try:
        cancel_appointment(appointment_id, current_user.patient_id)
        flash("Appointment cancelled successfully", "success")

    except ValueError as e:
        flash(str(e), "danger")
    except Error as e:
        flash(e.msg, "danger")
    except Exception:
        flash("Something went wrong", "danger")

    return redirect(request.referrer or url_for("patient.appointment_history"))


@patient_bp.route("/appointments/<int:appointment_id>")
@login_required
@role_required("Patient")
def appointment_details(appointment_id):
    appointment = get_appointment_details(appointment_id, current_user.patient_id)
    if not appointment:
        abort(404)

    return render_template("patient/appointment_details.html", appointment=appointment)

@patient_bp.route("/appointments/<int:appointment_id>/tests")
@login_required
@role_required("Patient")
def appointment_tests(appointment_id):
    tests = get_tests_of_appointment(appointment_id,current_user.patient_id)
    if tests is None:
        abort(404)

    return render_template("patient/appointment_tests.html", tests=tests, appointment_id=appointment_id)

