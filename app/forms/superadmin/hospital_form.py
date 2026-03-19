from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length, Regexp, Optional


class AddHospitalForm(FlaskForm):
    hospital_name = StringField("Hospital Name", validators=[DataRequired(), Length(max=150)])
    address = StringField("Address",validators=[Optional(), Length(max=500)])
    city = StringField("City",validators=[DataRequired(), Length(max=100)])
    state = StringField("State",validators=[DataRequired(), Length(max=100)])

    pincode = StringField("Pincode", validators=[DataRequired(),Regexp(r'^\d{6}$', message="Pincode must be 6 digits")])

    submit = SubmitField("Add Hospital")