from flask import Blueprint
labstaff_bp = Blueprint("labstaff", __name__, url_prefix="/lab")

from . import (
    dashboard_routes,
    profile_routes,
    report_routes,
    test_request_routes
)