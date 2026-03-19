from flask import render_template
from flask_login import login_required, current_user
from app.decorators.role_required import role_required
from app.services.admin.dashboard_service import get_admin_dashboard_stats
from . import admin_bp

@admin_bp.route("/dashboard")
@login_required
@role_required("Admin")
def dashboard():
    stats = get_admin_dashboard_stats(current_user.hospital_id)
    return render_template("admin/dashboard.html", stats=stats)

