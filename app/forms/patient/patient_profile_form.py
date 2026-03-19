from flask_wtf import FlaskForm
from wtforms import StringField, DateField, SelectField, SubmitField
from wtforms.validators import DataRequired, Email, Optional, Length, Regexp


class EditProfileForm(FlaskForm):
    def validate(self, extra_validators=None):
        if not super().validate(extra_validators):
            return False
        if not self.email.data and not self.phone.data:
            self.email.errors.append("Email or phone required")
            return False
        return True
    
    patient_name = StringField("Full Name", validators=[DataRequired(), Length(max = 100)])
    email = StringField("Email", validators=[Optional(), Email(), Length(max = 100)])
    phone = StringField("Phone",validators=[Optional(), Regexp(r'^\d{10}$', message="Phone must be 10 digits")])

    gender = SelectField("Gender",choices=[("Male", "Male"),("Female", "Female"),("Other", "Other")],validators=[DataRequired()])
    dob = DateField("Date of Birth", validators=[Optional()])
    address = StringField("Address",validators=[Optional(), Length(max = 500)])

    submit = SubmitField("Update Profile")