from flask_wtf import FlaskForm
from wtforms import SubmitField, PasswordField
from wtforms.validators import Length, DataRequired, EqualTo

class ChangePasswordForm(FlaskForm):
    current_password = PasswordField("Current Password", validators=[DataRequired(), Length(min=6)])
    new_password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo("new_password", "Confirm Password does not matches Password")])

    submit = SubmitField("Change Password")