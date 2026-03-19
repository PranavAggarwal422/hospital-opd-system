from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional

class AddHospitalTestForm(FlaskForm):
    test_type = SelectField(
        "Test Type",
        choices=[
            ("XRay", "XRay"),
            ("MRI", "MRI"),
            ("CT", "CT"),
            ("Ultrasound", "Ultrasound"),
            ("Blood", "Blood"),
            ("Urine", "Urine"),
            ("Other", "Other")
        ],
        validators=[DataRequired()]
    )

    test_name = StringField("Test Name", validators=[DataRequired(), Length(max=120)])
    test_description = TextAreaField("Description", validators=[Optional(), Length(max=250)])
    submit = SubmitField("Add Test")

