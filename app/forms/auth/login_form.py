from flask_wtf import FlaskForm
from wtforms import StringField , SubmitField, PasswordField
from wtforms.validators import Length, DataRequired, Email, ValidationError

class LoginForm(FlaskForm) : 
    def validate_email_or_phone(self, input_to_check) :
        email_validator =  Email() 

        # try validating as email 
        try : 
            email_validator(self, input_to_check)
            return 
        except ValidationError : 
            pass 
            
        # try validating as phone 
        if not(len(input_to_check.data) == 10 and input_to_check.data.isdigit()) : 
            raise ValidationError("Enter a valid email or phone number")

    email_or_phone = StringField(label = "Email or Phone", validators = [DataRequired()])
    password = PasswordField(label = "Password", validators = [DataRequired()])
    submit = SubmitField(label = "Login")

    @property
    def is_email(self) : 
        return "@" in self.email_or_phone.data