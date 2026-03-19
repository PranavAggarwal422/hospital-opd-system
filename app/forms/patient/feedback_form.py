from flask_wtf import FlaskForm
from wtforms import IntegerField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Optional, NumberRange

class FeedbackForm(FlaskForm):
    rating = IntegerField("Rating", validators=[DataRequired(message = "Please select a rating before submitting."),  NumberRange(min=1, max=5)])
    comment = TextAreaField("Comment", validators=[Optional()])
    submit = SubmitField("Submit Feedback")