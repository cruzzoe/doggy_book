from app import app
import datetime
from flask import render_template, flash, redirect, url_for, request, abort, send_from_directory
from flask_login import login_user, logout_user, current_user, login_required
from app.models import User, Dog, Slot
from werkzeug.urls import url_parse
from app.forms import RegistrationForm, LoginForm, RegistrationDogForm, ScheduleForm, EditDogForm, ResetPasswordForm, ResetPasswordRequestForm, BookingForm, RepeatScheduleForm
from app import db
from app.email_utils import send_password_reset_email, send_new_booking_email, send_cancellation_email, send_deletion_email
from app.enums import BOOKED, FREE
import os
import imghdr
import random

app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024
app.config['UPLOAD_EXTENSIONS'] = ['.jpg', '.jpeg']

if not app.debug:
    app.config['UPLOAD_PATH'] = '/dog_data/dog_service/uploads_dir'
else:
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['UPLOAD_PATH'] = os.path.join(basedir, 'uploads_dir')

app.config['CALENDAR_PATH'] = 'calendar_path'


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.datetime.utcnow()
        db.session.commit()

class Placeholder_dog():

    def __init__(self):
        self.dog_name = ''
        self.main_pic = '111.jpg'

@app.context_processor
def inject_gallery():
    next_url = None
    prev_url = None

    if current_user.is_authenticated:
        page = request.args.get('page', 1, type=int)
        display = True

        # Limit gallery size to 6 for now...
        dogs = Dog.query.paginate(page, 6, False)
        next_url = url_for('index', page=dogs.next_num, _anchor='portfolio') if dogs.has_next else None
        prev_url = url_for('index', page=dogs.prev_num, _anchor='portfolio') if dogs.has_prev else None

        pic_res = []
        for dog in dogs.items:
            pic_res.append((dog, dog.main_pic))
        display = True

        placeholder_dog = Placeholder_dog()
        count = 0
        while len(pic_res) < 6:
            placeholder_name = 'placeholder_' + str(count)
            pic_res.append((Placeholder_dog(), placeholder_dog.main_pic))
    else:
        display = False
        pic_res = None

    if not pic_res:
        display = False
    
    return dict(pic_res=pic_res, display=display, next_url=next_url, prev_url=prev_url)

def get_number_of_completed_bookings():
    slots = Slot.query.all()
    n_of_bookings = len([x for x in slots if x.status == BOOKED if datetime.datetime.strptime(x.date, '%Y-%m-%d').date() < datetime.date.today()])
    return n_of_bookings
    
def get_number_of_upcoming_bookings():
    """Booked upcoming session"""
    slots = Slot.query.all()
    n_of_bookings = len([x for x in slots if x.status == BOOKED if datetime.datetime.strptime(x.date, '%Y-%m-%d').date() >= datetime.date.today()])
    return n_of_bookings

def get_number_of_users():
    users = User.query.all()
    user_count = len([x for x in users])
    return user_count

def get_number_of_upcoming_available():
    slots = Slot.query.all()
    n_of_bookings = len([x for x in slots if x.status == FREE if datetime.datetime.strptime(x.date, '%Y-%m-%d').date() >= datetime.date.today()])
    return n_of_bookings

@app.route('/')
@app.route('/index')
@login_required
def index():
    number_of_bookings = get_number_of_completed_bookings()
    user_count = get_number_of_users()
    future_booked_count = get_number_of_upcoming_bookings()
    available_sessions = get_number_of_upcoming_available()
    return render_template('index.html', title='Home', number_of_bookings=number_of_bookings, user_count=user_count, future_booked_count=future_booked_count, available_sessions=available_sessions)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data.lower()).first()
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
        user = User(username=form.username.data.lower().strip(), email=form.email.data,
                    phone=form.phone.data,
                    first_name=form.first_name.data, last_name=form.last_name.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        login_user(user)
        return redirect(url_for('index'))
    return render_template('register.html', title='Register', form=form)


@app.route('/register_dog/', methods=['GET', 'POST'])
@login_required
def register_dog():
    """Submit your dog to the site"""
    form = RegistrationDogForm()
    if form.validate_on_submit():
        user_id = current_user
        dog = Dog(dog_name=form.dog_name.data, gender=form.gender.data, breed=form.breed.data, info=form.info.data, dob=form.dob.data, owner=user_id)
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

    form = EditDogForm()
    if form.validate_on_submit():
        user_id = current_user
        dog.dog_name = form.dog_name.data
        dog.gender = form.gender.data
        dog.breed = form.breed.data
        dog.info = form.info.data
        dog.dob = form.dob.data
        db.session.commit()
        flash('Dog Updated')
        return redirect(url_for('view_schedule'))
    
    elif request.method == 'GET':
        form.dog_name.data = dog.dog_name
        form.gender.data = dog.gender
        form.breed.data = dog.breed
        form.info.data = dog.info
        form.dob.data = dog.dob
    return render_template('edit_dog.html', title='Edit Dogs', form=form)

@app.route('/view_dogs')
@login_required
def view_dogs():
    dogs = Dog.query.all()
    res = []
    for dog in dogs:
        if dog.owner != current_user and len(dog.free_slots) !=0:
            res.append(dog)
    res.sort(key=lambda x: len(x.free_slots), reverse=True)
    return render_template('view_dogs.html', title='View Dogs', dogs=res)

@app.route('/book_dog')
@login_required
def book_dog():
    dog_name = request.args.get('dog_name')
    dog = Dog.query.filter_by(dog_name=dog_name).first()
    slots = dog.slots.all()
    slots = [x for x in slots if x.status != BOOKED]
    slots = [x for x in slots if datetime.datetime.strptime(x.date, '%Y-%m-%d').date() >= datetime.datetime.utcnow().date()]
    slots.sort(key=lambda x: x.date)
    picture = dog.main_pic
    return render_template('book_dog.html', title='Slot booked', dog=dog, slots=slots, picture=picture)

@app.route('/book_slot', methods=['GET', 'POST'])
@login_required
def book_slot():
    form = BookingForm()

    slot = request.args.get('slot')
    slot = Slot.query.filter_by(id=slot).first()
    dog_name = slot.subject.dog_name

    if form.validate_on_submit():
        user_id = current_user
        slot.comments = form.comments.data
        db.session.commit()
        return redirect(url_for('confirmed', slot=slot.id))

    return render_template('book_slot.html', title='Slot booked', slot=slot, dog_name=dog_name, form=form)

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
    send_cancellation_email(slot)
    slot.status = FREE
    slot.comments = ''
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

    if slot.booker is not None:
        send_deletion_email(slot)

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
    dog = Dog.query.filter_by(user_id=user_id).first()

    if not dog:
        # TODO Add flash message
        return redirect(url_for('view_schedule'))

    dog_name = dog.dog_name

    if form.validate_on_submit():
        user_id = current_user
        subject = Dog.query.filter_by(dog_name=dog.dog_name).first()
        slot = Slot(date=form.date.data, start=form.start.data, end=form.end.data, subject=subject, status=FREE, comments='')
        db.session.add(slot)
        db.session.commit()
        flash('Schedule amended')
        return redirect(url_for('view_schedule'))
    return render_template('new_slot.html', title='Amend your dogs availability', form=form, dog=dog.dog_name)

@app.route('/repeat_slot', methods=['GET', 'POST'])
@login_required
def repeat_slot():
    """Book a new slot for dogs owned by user"""
    user_id = current_user.id
    form = RepeatScheduleForm()
    dog = Dog.query.filter_by(user_id=user_id).first().dog_name

    if form.validate_on_submit():
        user_id = current_user
        subject = Dog.query.filter_by(dog_name=dog).first()
        selected_day = int(form.selected_days.data)
        repeats = form.repeats.data        
        # Starting from the selected day below, create slots up to the number specified in Slot Repeats (up to 10)
        dates = []
        count = 0
        date = datetime.date.today()
        while count < repeats:
            if date.weekday() == selected_day:
                slot = Slot(date=date, start=form.start.data, end=form.end.data, subject=subject, status=FREE, comments='')
                count += 1
            date += datetime.timedelta(days=1)
        
        db.session.add(slot)
        db.session.commit()
        return redirect(url_for('view_schedule'))
    return render_template('repeat_slot.html', title='Amend your dogs availability', form=form, dog=dog)

@app.route('/view_schedule')
@login_required
def view_schedule():
    """View slots existing for your dog"""
    user_id = current_user.id
    dog = Dog.query.filter_by(user_id=user_id).first()
    
    # TODO bug here. Displays the last dog of the user always.
    # Note at the moment we don't support more than one dog!
    if dog:
        picture = dog.main_pic
        slots = dog.slots.all()
        slots = [x for x in slots if datetime.datetime.strptime(x.date, '%Y-%m-%d').date() >= datetime.date.today()]
    else:
        picture = ''
        slots = []

    return render_template('schedule.html', title='View slots', dog=dog, slots=slots, picture=picture)

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

def get_file_extension(stream):
    header = stream.read(512)  # 512 bytes should be enough for a header check
    stream.seek(0)  # reset stream pointer
    file_format = imghdr.what(None, header)
    if not file_format:
        return None
    return '.' + (file_format if file_format != 'jpeg' else 'jpg')

@app.route('/upload_photo', methods=['GET', 'POST'])
@login_required
def upload_photo():
    if request.method == 'POST':
        uploaded_file = request.files['file']
        user_id = current_user
        dog = Dog.query.filter_by(owner=user_id).first()
        filename = str(dog.id)
        file_ext = get_file_extension(uploaded_file.stream)
        if file_ext not in app.config['UPLOAD_EXTENSIONS']:
            abort(400)
        uploaded_file.save(os.path.join(app.config['UPLOAD_PATH'], filename + '.jpeg'))
        return redirect(url_for('view_schedule'))
    else:
        return render_template('upload_photo.html')

@app.route('/uploads/<filename>')
@login_required
def upload(filename):
    return send_from_directory(app.config['UPLOAD_PATH'], filename)

# @app.route('/dog/<dog_id>')
# @login_required
# def show_dog(dog_id):
#     dog = Dog.query.filter_by(id=dog_id).first()
    
#     # check if picture exists
#     path = os.path.join('app', app.config['UPLOAD_PATH'], str(dog.id) + '.jpeg')
#     if os.path.exists(path):
#         picture = str(dog.id) + '.jpeg'
#     else:
#         picture = None
#     return render_template('dog.html', dog=dog, picture=picture)