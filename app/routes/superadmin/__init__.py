from flask import Blueprint
superadmin_bp = Blueprint("superadmin",__name__,url_prefix="/superadmin")

from . import (
    dashboard_routes,
    hospital_routes,
    admin_routes
)