from flask_wtf import FlaskForm
from wtforms import DateField, SubmitField
from wtforms.validators import DataRequired
from datetime import date


class BookAppointmentForm(FlaskForm):
    def validate(self, extra_validators=None):
        if not super().validate(extra_validators):
            return False

        if self.appointment_date.data < date.today():
            self.appointment_date.errors.append("Appointment date cannot be in the past")
            return False

        return True
    
    appointment_date = DateField("Appointment Date", validators=[DataRequired()])
    submit = SubmitField("Book Appointment")