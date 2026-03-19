from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length, Optional


class AddLabForm(FlaskForm):
    lab_name = StringField("Lab Name", validators=[DataRequired(), Length(max=100)])
    location = StringField("Location", validators=[Optional(), Length(max=200)])
    submit = SubmitField("Add Lab")

