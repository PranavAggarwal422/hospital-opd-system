from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length, Email, Optional, Regexp

class EditProfileForm(FlaskForm):
    name = StringField("Full Name", validators=[DataRequired(), Length(max = 100)])
    phone = StringField("Phone",validators=[Optional(), Regexp(r'^\d{10}$', message="Phone must be 10 digits")])
    submit = SubmitField("Update Profile")