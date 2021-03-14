from app import app
import os
import json
from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user, current_user, login_required
from app.models import User, Dog, Slot
from werkzeug.urls import url_parse
from app.forms import RegistrationForm, LoginForm, RegistrationDogForm, ScheduleForm
from app import db

@app.route('/')
@app.route('/index')
@login_required
def index():
    return render_template('index.html', title='Home')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

def save_down_dog(form):
    """Given form, save down data as json"""

    # make a dict to save info and save down as json
    data = {'dog_name': str(form.dogname.data),
            'owner': str(form.personname.data),
            'phone': str(form.phone.data),
            'email': str(form.email.data)}
    data_dir = os.environ['DATA_DIR']
    file_path = os.path.join(data_dir, str(form.email.data) + '.json')
    with open(file_path, 'wt') as outfile:
        json.dump(data, outfile)


# @app.route('/register_dog', methods=['GET', 'POST'])
# def register():
#     form = RegisterForm()
#     if form.validate_on_submit():
#         # flash('Login requested for user {}, remember_me={}'.format(
#             # form.username.data, form.remember_me.data))

#         # Save down new dog info to AWS
#         save_down_dog(form)
#         flash('Dog Registered: {}'.format(form.dogname.data))
#         return redirect('/index')
#     return render_template('register.html', title='Register Dog', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('register_dog'))
    return render_template('register.html', title='Register', form=form)

@login_required
@app.route('/register_dog/', methods=['GET', 'POST'])
def register_dog():
    """Submit your dog to the site"""
    form = RegistrationDogForm()
    if form.validate_on_submit():
        user_id = current_user
        dog = Dog(dog_name=form.dog_name.data, gender=form.gender.data, age=form.age.data, owner=user_id)
        db.session.add(dog)
        db.session.commit()
        flash('Congratulations, you\'re dog is now on the site!')
        return redirect(url_for('index'))
    return render_template('register_dog.html', title='Register', form=form)

# @login_required
# @app.route('/enter_slots', methods=['GET', 'POST'])
# def enter_slots():
#     """Pick a slot for when the dog is free"""
#     form = FreeSlotsForm()
#     if form.validate_on_submit():
#         user = User(username=form.username.data, email=form.email.data)
#         user.set_password(form.password.data)
#         db.session.add(user)
#         db.session.commit()
#         flash('Congratulations, you\'re dog is now on the site!')
#         return redirect(url_for('index'))
#     return render_template('register.html', title='Register', form=form)


# def load_available_dogs():
#     data_dir = os.environ['DATA_DIR']
#     dogs = os.listdir(data_dir)
#     res = []
#     for fname in dogs:
#         path = os.path.join(data_dir, fname)
#         with open(path) as json_file:
#             data = json.load(json_file)
#             res.append(data)
#     return res


# @app.route('/')
# @app.route('/view_dogs')
# def view_dogs():
#     dogs = load_available_dogs()
#     return render_template('view_dogs.html', title='View Dogs', dogs=dogs)

@app.route('/view_dogs')
def view_dogs():
    # dogs = load_available_dogs()
    dogs = Dog.query.all()
    return render_template('view_dogs.html', title='View Dogs', dogs=dogs)

@app.route('/schedule', methods=['GET', 'POST'])
def schedule():
    # Display all your dogs
    # Who are you?

    # Load dogs belonging to you
    # For dog belonging to you enter in new schedule
    # dogs = Dog.query.all()
    # user = User.query.get(id)
    user_id = current_user.id
    form = ScheduleForm()
    dogs = [dog.dog_name for dog in Dog.query.filter_by(user_id=user_id)]
    form.dog.choices = dogs

    if form.validate_on_submit():
        user_id = current_user
        subject = Dog.query.filter_by(dog_name=form.dog.data).first()
        
        slot = Slot(date=form.date.data, start=form.start.data, end=form.end.data, subject=subject)
        db.session.add(slot)
        db.session.commit()
        flash('Schedule amended')
        return redirect(url_for('index'))
    return render_template('schedule.html', title='Amend your dogs availability', form=form)

@app.route('/book_dog')
def book_dog():
    dog_name = request.args.get('dog_name')
    dog = Dog.query.filter_by(dog_name=dog_name).first()
    slots = dog.slots.all()
    return render_template('book_dog.html', title='Slot booked', dog=dog, slots=slots)

@app.route('/book_slot')
def book_slot():
    slot = request.args.get('slot')
    slot = Slot.query.filter_by(id=slot).first()
    dog_name = slot.subject.dog_name
    return render_template('book_slot.html', title='Slot booked', slot=slot, dog_name=dog_name)

@app.route('/confirmed')
def confirmed():
    flash('You\'r booking is confirmed! A text msg has been sent to both parties.')
    slot = request.args.get('slot')
    # import pdb; pdb.set_trace()
    slot = Slot.query.filter_by(id=slot).first()
    slot.booker = current_user
    slot.status = 'BOOKED'
    db.session.add(slot)
    db.session.commit()
    return  redirect(url_for('index'))