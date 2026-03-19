from flask import Blueprint
admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

from . import (
    dashboard_routes,
    profile_routes,
    department_routes,
    doctor_routes,
    opd_routes,
    session_routes,
    lab_routes,
    labstaff_routes,
    test_routes
)