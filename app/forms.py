from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from app.models import User

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

# class RegisterForm(FlaskForm):
#     dogname = StringField('Dog Name', validators=[DataRequired()])
#     personname = StringField('Your Name', validators=[DataRequired()])
#     phone = StringField('Phone', validators=[DataRequired()])
#     email = StringField('Email', validators=[DataRequired()])
#     submit = SubmitField('Register')

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
    gender = StringField('Gender', validators=[DataRequired()])
    age = StringField('Age', validators=[DataRequired()])
    submit = SubmitField('Submit')
    
class ScheduleForm(FlaskForm):
    # dog = SelectField('Selected Dog: ', default='dogA',choices=['dogA'])
    dog = SelectField('Selected Dog: ')
    date = StringField('Date dd/mm/yy', validators=[DataRequired()])
    start = StringField('Start time (24hr)', validators=[DataRequired()])
    end = StringField('End time (24hr)', validators=[DataRequired()])
    submit = SubmitField('Submit')

