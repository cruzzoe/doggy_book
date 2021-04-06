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
    comments = TextAreaField('Booking Comments (will be included in booking email)', validators=[Length(min=0, max=10000)])
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
    now = datetime.date.today()
    # TODO bug here. date doesnt update meaning values are stuck from when service last started.
    # Move this to routes.py
    # https://github.com/miguelgrinberg/microblog/issues/143
    choices = []
    for delta in range(0, 15):
        choices.append(now + datetime.timedelta(days=delta))
    date = SelectField('Date: ', choices=choices, validate_choice=True)
    
    choices = list(range(0, 24))
    choices = [str(x) + ':00' for x in choices]
    start = SelectField('Start time (24hr)', choices=choices, default='9:00', validate_choice=True)
    end = SelectField('End time (24hr)', choices=choices, validate_choice=True, default='10:00')
    submit = SubmitField('Submit')

class RepeatScheduleForm(FlaskForm):
    now = datetime.date.today()
    choices = []
    days = [(0,'Monday'), (1,'Tuesday'), (2,'Wednesday'),(3,'Thursday'),(4,'Friday'),(5,'Saturday'),(6,'Sunday')]
    selected_days = SelectField('Day: ', choices=days, validate_choice=True)
    repeats = IntegerField('Number of weeks to repeat slot:')

    choices = list(range(0, 24))
    choices = [str(x) + ':00' for x in choices]
    start = SelectField('Start time (24hr)', choices=choices, default='9:00', validate_choice=True)
    end = SelectField('End time (24hr)', choices=choices, validate_choice=True, default='10:00')
    submit = SubmitField('Submit')

    def validate_repeats(self, repeats):
        if int(repeats.data) not in range(1, 11):
            raise ValidationError('Please enter a repeat value between 1 & 10')

class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Request Password Reset')

class DogBlastForm(FlaskForm):
    now = datetime.date.today()
    choices = []
    for delta in range(0, 15):
        choices.append(now + datetime.timedelta(days=delta))
    date = SelectField('Date: ', choices=choices, validate_choice=True)
    
    choices = list(range(0, 24))
    choices = [str(x) + ':00' for x in choices]
    start = SelectField('Start time (24hr)', choices=choices, default='9:00', validate_choice=True)
    end = SelectField('End time (24hr)', choices=choices, validate_choice=True, default='10:00')
    info = TextAreaField('Comments', validators=[Length(min=0, max=100000)])
    submit = SubmitField('Submit')

class DogBlastContacts(FlaskForm):
    user = SelectField('User', validate_choice=True)
    submit = SubmitField('Add User')

class WithdrawBlast(FlaskForm):
    submit = SubmitField('Withdraw Blast')