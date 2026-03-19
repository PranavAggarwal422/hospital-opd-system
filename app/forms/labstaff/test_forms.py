from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, DateField, FileField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, ValidationError, Optional , Length


class CreateTestRequestForm(FlaskForm):
    def validate_email_or_phone(self, field) :
        email_validator =  Email() 
        # try validating as email 
        try : 
            email_validator(self, field)
            return 
        except ValidationError : 
            pass 
        # try validating as phone 
        if not(len(field.data) == 10 and field.data.isdigit()) : 
            raise ValidationError("Enter a valid email or phone number")
        
    email_or_phone = StringField("Patient Email or Phone", validators=[DataRequired()])
    department_id = SelectField("Department", coerce=int, validators=[DataRequired()])
    appointment_date = DateField("Appointment Date", validators=[DataRequired()])
    test_id = SelectField("Test", coerce=int, validators=[DataRequired()])
    submit = SubmitField("Create Test Request")

    @property
    def is_email(self) : 
        return "@" in self.email_or_phone.data




class UploadReportForm(FlaskForm):
    report_url = FileField("Upload Report", validators=[DataRequired()])
    remarks = TextAreaField("Remarks", validators=[Optional(), Length(max=255)])
    submit = SubmitField("Upload Report")

