from flask import render_template, abort, flash, redirect ,url_for
from flask_login import login_required, current_user
from app.decorators.role_required import role_required
from app.services.patient.appointment_service import get_appointment_details
from app.services.patient.feedback_service import *
from app.forms.patient.feedback_form import FeedbackForm
from app.routes.helpers import flash_form_errors
from . import patient_bp

@patient_bp.route("/appointments/<int:appointment_id>/feedback", methods=["GET","POST"])
@login_required
@role_required("Patient")
def appointment_feedback(appointment_id):
    patient_id = current_user.patient_id
    appointment = get_appointment_details(appointment_id, patient_id)

    if not appointment:
        abort(404)

    if appointment["appointment_status"] != "Expired":
        flash("Feedback can only be submitted after appointment completion","warning")
        return redirect(url_for("patient.appointment_details", appointment_id=appointment_id))

    existing = get_feedback_by_appointment(appointment_id, patient_id)

    if existing:
        flash("Feedback already submitted","info")
        return redirect(url_for("patient.appointment_details", appointment_id=appointment_id))

    form = FeedbackForm()

    if form.validate_on_submit():
        data = {
            "appointment_id": appointment_id,
            "rating": form.rating.data,
            "comment": form.comment.data.strip() or None
        }

        try:
            submit_feedback(data)
            flash("Feedback submitted successfully","success")
        except Exception:
            flash("Something went wrong","danger")
        return redirect(url_for("patient.appointment_details", appointment_id=appointment_id))
    
    if form.errors : 
        flash_form_errors(form)
        return redirect(url_for("patient.appointment_feedback", appointment_id=appointment_id))

    return render_template("patient/feedback.html", form=form, appointment=appointment)

