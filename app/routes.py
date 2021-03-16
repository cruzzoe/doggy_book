from app import app
import os
import json
from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user, current_user, login_required
from app.models import User, Dog, Slot
from werkzeug.urls import url_parse
from app.forms import RegistrationForm, LoginForm, RegistrationDogForm, ScheduleForm
from app import db

BOOKED = 'BOOKED'

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
        login_user(user)
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

@app.route('/view_dogs')
def view_dogs():
    dogs = Dog.query.all()
    res = []
    for dog in dogs:
        if dog.owner != current_user:
            res.append(dog)
    # import pdb; pdb.set_trace()
    return render_template('view_dogs.html', title='View Dogs', dogs=res)

@app.route('/book_dog')
def book_dog():
    dog_name = request.args.get('dog_name')
    dog = Dog.query.filter_by(dog_name=dog_name).first()
    slots = dog.slots.all()
    slots = [x for x in slots if x.status != BOOKED]
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
    slot.status = BOOKED
    db.session.add(slot)
    db.session.commit()
    return  redirect(url_for('index'))

@app.route('/my_bookings')
def my_bookings():
    return  redirect(url_for('index'))

@app.route('/cancel')
def cancel():
    """Cancels a booking"""
    return  redirect(url_for('index'))


@app.route('/delete_slot')
def delete_slot():
    slot = request.args.get('slot')
    slot = Slot.query.filter_by(id=slot).first()
    db.session.delete(slot)
    db.session.commit()
    flash('Slot deleted')
    return  redirect(url_for('view_schedule'))


@app.route('/new_slot', methods=['GET', 'POST'])
def new_slot():
    """Book a new slot for dogs owned by user"""
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
    return render_template('new_slot.html', title='Amend your dogs availability', form=form)

@app.route('/view_schedule')
def view_schedule():
    """View slots existing for your dog"""
    user_id = current_user.id
    dogs = [dog for dog in Dog.query.filter_by(user_id=user_id)]
    return render_template('schedule.html', title='View slots', dogs=dogs)

@app.route('/bookings')
def bookings():
    """View user bookings made for others dogs"""
    # dogs = Dog.query.all()
    # res = []
    # for dog in dogs:
    #     if dog.owner != current_user:
    #         res.append(dog.slots)

    slots = Slot.query.filter_by(booking_user=current_user.id).all()
    import pdb; pdb.set_trace()
    return render_template('bookings.html', title='View slots', slots=slots)
