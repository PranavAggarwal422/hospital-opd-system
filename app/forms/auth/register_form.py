from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, DateField, SelectField
from wtforms.validators import DataRequired, Length, Email, Optional, EqualTo, Regexp, ValidationError
from datetime import date 

class PatientRegisterForm(FlaskForm):
    def validate(self, extra_validators=None):
        if not super().validate(extra_validators):
            return False
        if not self.email.data and not self.phone.data:
            self.email.errors.append("Email or phone required")
            return False
        return True
    
    def validate_dob(self, field):
        if field.data:
            today = date.today()
            if field.data > today:
                raise ValidationError("Enter a valid date of birth")
    
    
    patient_name = StringField("Full Name", validators=[DataRequired(), Length(max = 100)])
    email = StringField("Email", validators=[Optional(), Email(), Length(max = 100)])
    phone = StringField("Phone",validators=[Optional(), Regexp(r'^\d{10}$', message="Phone must be 10 digits")])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])

    confirm_password = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo("password", "Confirm Password does not matches Password")])

    gender = SelectField("Gender",choices=[("Male","Male"),("Female","Female"),("Other","Other")], validators=[DataRequired()])

    dob = DateField("Date of Birth", validators=[Optional()])
    address = StringField("Address",validators=[Optional(), Length(max = 500)])
    submit = SubmitField("Register")