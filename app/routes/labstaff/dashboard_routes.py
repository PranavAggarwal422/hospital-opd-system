from flask import render_template
from flask_login import login_required, current_user
from app.decorators.role_required import role_required
from app.services.labstaff.dashboard_service import get_lab_dashboard_stats
from . import labstaff_bp


@labstaff_bp.route("/dashboard")
@login_required
@role_required("LabStaff")
def dashboard():
    stats = get_lab_dashboard_stats(current_user.lab_id)
    return render_template("lab/dashboard.html", stats=stats)
