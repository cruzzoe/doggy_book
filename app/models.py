from datetime import datetime
from app import db, login, app
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from sqlalchemy.ext.hybrid import hybrid_property
from time import time
import jwt

from app.enums import BOOKED, FREE

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    first_name = db.Column(db.String(64), index=True)
    last_name = db.Column(db.String(64), index=True)
    phone = db.Column(db.Integer)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    dogs = db.relationship('Dog', backref='owner', lazy='dynamic')
    booking_slot = db.relationship('Slot', backref='booker', lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)

class Dog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dog_name = db.Column(db.String(140), unique=True)
    dob = db.Column(db.Date)
    info = db.Column(db.Text())
    gender = db.Column(db.String(140))
    breed = db.Column(db.String(140))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    slots = db.relationship('Slot', backref='subject', lazy='dynamic')

    @hybrid_property
    def free_slots(self):
        # TODO - bug here. Doesn't respect times of slot when calculating free slot.
        # TODO should return an int. Not a list of free slots.
        slots = [x for x in self.slots.all() if x.status != BOOKED and datetime.strptime(x.date, '%Y-%m-%d').date() >= datetime.utcnow().date()]
        return slots

    @hybrid_property
    def age(self):
        return self.dob.strftime("%Y-%m-%d")

    def __repr__(self):
        return '<Dog {}>'.format(self.dog_name)

class Slot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(140))
    start = db.Column(db.String(140))
    end = db.Column(db.String(140))
    status = db.Column(db.String(140))
    dog_id = db.Column(db.Integer, db.ForeignKey('dog.id'))
    booking_user = db.Column(db.Integer, db.ForeignKey('user.id'))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def __repr__(self):
        return '<Slot {}>'.format(str(self.id))

    @hybrid_property
    def day_str(self):
        return datetime.strptime(self.date, "%Y-%M-%d").date().strftime('%A')
