from app import app
import datetime
from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user, current_user, login_required
from app.models import User, Dog, Slot
from werkzeug.urls import url_parse
from app.forms import RegistrationForm, LoginForm, RegistrationDogForm, ScheduleForm
from app import db
from app.forms import ResetPasswordForm, ResetPasswordRequestForm
from app.email import send_password_reset_email, send_new_booking_email
from app.enums import BOOKED, FREE


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
    """Register a new user"""
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


@app.route('/register_dog/', methods=['GET', 'POST'])
@login_required
def register_dog():
    """Submit your dog to the site"""
    form = RegistrationDogForm()
    if form.validate_on_submit():
        user_id = current_user
        dog = Dog(dog_name=form.dog_name.data, gender=form.gender.data, info=form.info.data, age=form.age.data, owner=user_id)
        db.session.add(dog)
        db.session.commit()
        flash('Congratulations, you\'re dog is now on the site!')
        return redirect(url_for('view_schedule'))
    return render_template('register_dog.html', title='Register', form=form)

@app.route('/edit_dog/', methods=['GET', 'POST'])
@login_required
def edit_dog():
    """Submit your dog to the site"""
    user_id = current_user
    dog = Dog.query.filter_by(owner=user_id).first()

    if not dog:
        return redirect(url_for('register_dog'))

    form = RegistrationDogForm()
    if form.validate_on_submit():
        user_id = current_user
        dog.dog_name = form.dog_name.data
        dog.gender = form.gender.data
        dog.info = form.info.data
        dog.age = form.age.data
        db.session.commit()
        flash('Dog Updated')
        return redirect(url_for('view_schedule'))
    
    elif request.method == 'GET':
        form.dog_name.data = dog.dog_name
        form.gender.data = dog.gender
        form.info.data = dog.info
        form.age.data = dog.age
    return render_template('edit_dog.html', title='Edit Dogs', form=form)

@app.route('/view_dogs')
@login_required
def view_dogs():
    dogs = Dog.query.all()
    res = []
    for dog in dogs:
        if dog.owner != current_user:
            res.append(dog)
    # import pdb; pdb.set_trace()
    return render_template('view_dogs.html', title='View Dogs', dogs=res)

@app.route('/book_dog')
@login_required
def book_dog():
    dog_name = request.args.get('dog_name')
    dog = Dog.query.filter_by(dog_name=dog_name).first()
    slots = dog.slots.all()
    slots = [x for x in slots if x.status != BOOKED]
    slots = [x for x in slots if datetime.datetime.strptime(x.date, '%Y-%m-%d').date() >= datetime.datetime.utcnow().date()]
    return render_template('book_dog.html', title='Slot booked', dog=dog, slots=slots)

@app.route('/book_slot')
@login_required
def book_slot():
    slot = request.args.get('slot')
    slot = Slot.query.filter_by(id=slot).first()
    dog_name = slot.subject.dog_name
    return render_template('book_slot.html', title='Slot booked', slot=slot, dog_name=dog_name)

@app.route('/confirmed')
@login_required
def confirmed():
    flash('You\'r booking is confirmed! An email has been sent to both parties.')
    slot = request.args.get('slot')
    slot = Slot.query.filter_by(id=slot).first()
    slot.booker = current_user
    slot.status = BOOKED
    db.session.add(slot)
    db.session.commit()
    send_new_booking_email(slot)
    return  redirect(url_for('bookings'))

@app.route('/cancel_slot')
@login_required
def cancel_slot():
    """Cancel booking and make available again for other users to book."""
    slot = request.args.get('slot')
    slot = Slot.query.filter_by(id=slot).first()
    slot.status = FREE
    slot.booker = None
    db.session.commit()
    # TODO Deb - doesn't display flash msg.
    flash('Slot status cleared')
    return redirect(url_for('bookings'))

@app.route('/delete_slot')
@login_required
def delete_slot():
    slot = request.args.get('slot')
    slot = Slot.query.filter_by(id=slot).first()
    db.session.delete(slot)
    db.session.commit()
    flash('Slot deleted')
    return redirect(url_for('view_schedule'))

@app.route('/new_slot', methods=['GET', 'POST'])
@login_required
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
        return redirect(url_for('view_schedule'))
    return render_template('new_slot.html', title='Amend your dogs availability', form=form)

@app.route('/view_schedule')
@login_required
def view_schedule():
    """View slots existing for your dog"""
    user_id = current_user.id
    dogs = Dog.query.filter_by(user_id=user_id).all()
    return render_template('schedule.html', title='View slots', dogs=dogs)

@app.route('/bookings')
@login_required
def bookings():
    """View user bookings made for others dogs"""
    slots = Slot.query.filter_by(booking_user=current_user.id).all()
    slots = [x for x in slots if x.status == BOOKED]
    return render_template('bookings.html', title='View slots', slots=slots)

@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    """Serves the form to request password reset"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('Check your email for the instructions to reset your password')
        return redirect(url_for('login'))
    return render_template('reset_password_request.html',
                           title='Reset Password', form=form)

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Client submits token requesting password reset"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)