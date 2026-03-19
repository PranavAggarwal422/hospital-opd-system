from flask import render_template, redirect, flash, url_for
from flask_login import login_user, logout_user, login_required, current_user
from app.forms.auth.login_form import LoginForm
from app.forms.auth.register_form import PatientRegisterForm
from app.forms.auth.password_form import ChangePasswordForm
from app import bcrypt, User 
from app.services.auth.auth_service import *
from app.routes.helpers import flash_form_errors
from . import auth_bp

@auth_bp.route("/login", methods = ["GET", "POST"])
def login() : 
    login_form = LoginForm()
    if(login_form.validate_on_submit()) : 
        email_or_phone = login_form.email_or_phone.data.strip()
        password = login_form.password.data 
        if(login_form.is_email) : 
            user = get_user_by_email(email_or_phone)
        else : 
            user = get_user_by_phone(email_or_phone)
        
        if(user and bcrypt.check_password_hash(user["password_hash"], password)): 
            if user["user_status"] != "Active":
                flash("Account is currently disabled", category = "danger")
                return redirect(url_for("auth.login"))
            
            user_obj = User(user)
            login_user(user_obj)
            role = user["user_role"]
            if role == "Admin" : 
                 return redirect(url_for('admin.dashboard'))
            elif role == "Doctor":
                return redirect(url_for('doctor.dashboard'))
            elif role == "Patient":
                return redirect(url_for('patient.dashboard'))
            elif role == "LabStaff":
                return redirect(url_for('labstaff.dashboard'))
            elif role == "SuperAdmin" : 
                return redirect(url_for('superadmin.dashboard'))
        
        flash("Invalid Credentials", category = "danger")
        return redirect(url_for("auth.login"))

    if(login_form.errors != {}) : 
        flash_form_errors(login_form)
        return redirect(url_for("auth.login"))
    
    return render_template("auth/login.html", form = login_form)

@auth_bp.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("auth.login"))


@auth_bp.route("/register/patient", methods=["GET", "POST"])
def register_patient_route():
    form = PatientRegisterForm()

    if form.validate_on_submit():
        password_hash = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        # atleast one of email or phone is not empty ensured by validate_on_submit
        data = {
            "email": form.email.data.strip() or None,
            "phone": form.phone.data.strip() or None,
            "password_hash": password_hash,
            "patient_name": form.patient_name.data,
            "gender": form.gender.data,
            "dob": form.dob.data or None,
            "address": form.address.data.strip() or None 
        }

        try : 
            user_id = register_patient(data)
            flash("Registration successful", "success")
            return redirect(url_for("auth.login"))
        
        except ValueError as e:
            flash(str(e), "danger")
            return redirect(url_for('auth.login'))

        except Exception:
            flash("Something went wrong. Please try again.", "danger")
            return redirect(url_for('auth.register_patient_route'))
        
    if form.errors:
        flash_form_errors(form)
        return redirect(url_for("auth.register_patient_route"))

    return render_template("auth/patient_register.html", form=form)


@auth_bp.route("/profile/change-password", methods=["GET", "POST"])
@login_required
def change_password():
    form = ChangePasswordForm()

    # Decide layout and back button
    if current_user.user_role == "Admin":
        layout = "layouts/admin_layout.html"
        back_url = url_for("admin.profile")

    elif current_user.user_role == "Patient":
        layout = "layouts/patient_layout.html"
        back_url = None
    
    elif current_user.user_role == "LabStaff" : 
        layout = "layouts/lab_layout.html"
        back_url = url_for("labstaff.profile")
    
    elif current_user.user_role == "Doctor" : 
        layout = "layouts/doctor_layout.html"
        back_url = url_for("doctor.profile")

    else:
        layout = "base.html"
        back_url = None
        
    if form.validate_on_submit():
        try:
            user = get_user_by_id(current_user.id)

            # Verify current password
            if not bcrypt.check_password_hash(user["password_hash"], form.current_password.data):
                flash("Current password incorrect", "danger")
                return redirect(url_for("auth.change_password"))

            password_hash = bcrypt.generate_password_hash(form.new_password.data).decode("utf-8")
            update_user_password(current_user.id, password_hash)
            flash("Password updated successfully", "success")
            return redirect(back_url or url_for("auth.login"))

        except Exception as e :
            flash(str(e), "danger")
            return redirect(url_for("auth.change_password"))

    if form.errors:
        flash_form_errors(form)
        return redirect(url_for("auth.change_password"))

    return render_template("auth/change_password.html", form=form, layout=layout, back_url=back_url)


