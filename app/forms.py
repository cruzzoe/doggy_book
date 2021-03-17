from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, TextAreaField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length
from app.models import User
import datetime

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

class RegistrationDogForm(FlaskForm):
    dog_name = StringField('Dog Name', validators=[DataRequired()])
    gender = SelectField('Gender', choices=['Male', 'Female'], validate_choice=True)
    info = TextAreaField('Essential Info', validators=[Length(min=0, max=140)])
    age = SelectField('Age', choices=list(range(1, 21)), validate_choice=True)
    submit = SubmitField('Submit')

class ScheduleForm(FlaskForm):
    dog = SelectField('Selected Dog: ', validate_choice=True)
    now = datetime.date.today()
    choices = []
    for delta in range(0, 15):
        choices.append(now + datetime.timedelta(days=delta))
    date = SelectField('Date: ', choices=choices, validate_choice=True)
    
    choices = list(range(0, 23))
    choices = [str(x) + ':00' for x in choices]
    # for delta in range(0, 15):
    #     choices.append(now + datetime.timedelta(days=delta))
    start = SelectField('Start time (24hr)', choices=choices, validate_choice=True)
    # end = StringField('End time (24hr)', validators=[DataRequired()])
    end = SelectField('End time (24hr)', choices=choices, validate_choice=True)
    submit = SubmitField('Submit')

