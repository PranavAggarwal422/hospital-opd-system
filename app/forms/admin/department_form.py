from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length


class AddDepartmentForm(FlaskForm):
    department_name = StringField("Department Name", validators=[DataRequired(), Length(max=100)])
    submit = SubmitField("Add Department")