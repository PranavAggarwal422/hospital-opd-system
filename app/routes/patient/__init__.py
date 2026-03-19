from flask import Blueprint
patient_bp = Blueprint("patient", __name__, url_prefix="/patient")

from . import (
    appointment_routes,
    dashboard_routes,
    feedback_routes,
    hospital_routes,
    profile_routes,
    report_routes
)