from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, TextAreaField, DateField, IntegerField, FileField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length
from app.models import User, Dog
import datetime

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class BookingForm(FlaskForm):
    comments = TextAreaField('Booking Comments', validators=[Length(min=0, max=10000)])
    submit = SubmitField('Confirm Booking')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    phone = IntegerField('Phone Number', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data.strip()).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

class RegistrationDogForm(FlaskForm):
    dog_name = StringField('Dog Name', validators=[DataRequired()])
    gender = SelectField('Gender', choices=['Male', 'Female'], validate_choice=True)
    breed = StringField('Breed', validators=[DataRequired()])
    info = TextAreaField('Essential Info', validators=[Length(min=0, max=100000)])
    dob = DateField('Date of Birth', format='%d-%m-%Y', default=datetime.date(2019,12,1))
    submit = SubmitField('Submit')

    def validate_dog_name(self, dog_name):
        dog_name = Dog.query.filter_by(dog_name=dog_name.data).first()
        if dog_name is not None:
            raise ValidationError('This dog name is already taken!')

class EditDogForm(FlaskForm):
    dog_name = StringField('Dog Name', validators=[DataRequired()])
    gender = SelectField('Gender', choices=['Male', 'Female'], validate_choice=True)
    breed = StringField('Breed', validators=[DataRequired()])
    info = TextAreaField('Essential Info', validators=[Length(min=0, max=140)])
    dob = DateField('Date of Birth', format='%d-%m-%Y', default=datetime.date(2019,12,1))
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
    start = SelectField('Start time (24hr)', choices=choices, default='9:00', validate_choice=True)
    # end = StringField('End time (24hr)', validators=[DataRequired()])
    end = SelectField('End time (24hr)', choices=choices, validate_choice=True, default='10:00')
    submit = SubmitField('Submit')

class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Request Password Reset')