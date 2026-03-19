from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, TimeField, IntegerField, SubmitField
from wtforms.validators import DataRequired, NumberRange, Optional, Email, Regexp, ValidationError, Length

class AddOPDForm(FlaskForm):
    room_no = StringField("Room Number",validators=[DataRequired(), Length(max=10)])
    submit = SubmitField("Add OPD Room")

class AddSessionForm(FlaskForm):
    def validate(self, extra_validators=None):
        if not super().validate(extra_validators):
            return False
        if self.start_time.data >= self.end_time.data:
            self.end_time.errors.append("End time must be later than start time")
            return False
        return True
    
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
        
    week_day = SelectField("Day",
        choices=[
            ("Monday","Monday"),
            ("Tuesday","Tuesday"),
            ("Wednesday","Wednesday"),
            ("Thursday","Thursday"),
            ("Friday","Friday"),
            ("Saturday","Saturday"),
            ("Sunday","Sunday")
        ],
        validators=[DataRequired()]
    )

    start_time = TimeField("Start Time", validators=[DataRequired()])
    end_time = TimeField("End Time", validators=[DataRequired()])
    max_tokens = IntegerField("Max Tokens", default=50, validators=[DataRequired(), NumberRange(min=1)])
    email_or_phone = StringField(label = "Doctor Email or Phone", validators = [DataRequired()])
    submit = SubmitField("Create Session")
    
    @property
    def is_email(self) : 
        return "@" in self.email_or_phone.data