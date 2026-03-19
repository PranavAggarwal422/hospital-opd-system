from flask_wtf import FlaskForm
from wtforms import StringField, SelectField,PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, Optional, Email, Regexp, EqualTo

class AddLabStaffForm(FlaskForm):
    def validate(self, extra_validators=None):
        if not super().validate(extra_validators):
            return False

        if not self.email.data and not self.phone.data:
            self.email.errors.append("Email or phone required")
            return False

        return True
     
    staff_name = StringField("Staff Name", validators=[DataRequired(), Length(max=100)])

    staff_role = SelectField("Role",
        choices=[
            ("Technician", "Technician"),
            ("Receptionist", "Receptionist"),
            ("Manager", "Manager")
        ],
        validators=[DataRequired()]
    )

    email = StringField("Email", validators=[Optional(), Email(), Length(max=100)])
    phone = StringField("Phone", validators=[Optional(), Regexp(r'^\d{10}$', message="Phone must be 10 digits")])

    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo("password", "Confirm Password does not matches Password")])

    submit = SubmitField("Add Staff")


