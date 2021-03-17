from datetime import datetime
from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from sqlalchemy.ext.hybrid import hybrid_property

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
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

class Dog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dog_name = db.Column(db.String(140))
    age = db.Column(db.String(140))
    gender = db.Column(db.String(140))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    slots = db.relationship('Slot', backref='subject', lazy='dynamic')

    @hybrid_property
    def free_slots(self):
        # TODO - bug here. Doesn't respect times of slot when calculating free slot.
        slots = [x for x in self.slots.all() if x.status is None and datetime.strptime(x.date, '%Y-%m-%d').date() >= datetime.utcnow().date()]
        return slots

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