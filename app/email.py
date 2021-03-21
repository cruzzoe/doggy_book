from flask_mail import Message
from app import mail
from app import app
from flask import render_template
from threading import Thread
import os
from ics import Calendar, Event
import datetime


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

def send_email(subject, sender, recipients, text_body, html_body, attachment_path=None):
    if not app.debug:
        msg = Message(subject, sender=sender, recipients=recipients)
        msg.body = text_body
        msg.html = html_body

        if attachment_path:
            name = attachment_path.split('/')[-1]
            with app.open_resource(attachment_path) as fp:
                msg.attach(name, "type/calendar", fp.read())

        Thread(target=send_async_email, args=(app, msg)).start()

def send_password_reset_email(user):
    token = user.get_reset_password_token()
    send_email('Reset Your Password',
               sender=app.config['ADMINS'][0],
               recipients=[user.email],
               text_body=render_template('email/reset_password.txt',
                                         user=user, token=token),
               html_body=render_template('email/reset_password.html',
                                         user=user, token=token))

def create_calendar_file(slot):
    """From the slot obj, create a cal ics file."""
    c = Calendar()
    e = Event()
    slot_id = slot.id

    dog_name = slot.subject.dog_name
    date = slot.date
    start = slot.start
    end = slot.end

    # check if start in correct format
    first_val = start.split(':')[0]
    if len(first_val) == 1:
        start = '0' + start

    # check if end in correct format
    first_val = end.split(':')[0]
    if len(first_val) == 1:
        end = '0' + end

    # date_time = date.strftime('%Y-%m-%d')
    start_str = date + ' ' + start + ':00'
    end_str = date + ' ' + end + ':00'
    e.name = "Dog Booker: " + dog_name
    e.begin = start_str
    e.end = end_str
    e.description = 'Please co-ordinate a dog sitting!'
    c.events.add(e)
    dir_path = os.path.join('app', app.config['CALENDAR_PATH'])
    if not os.path.exists(dir_path):
        os.mkdir(dir_path)

    file_path = os.path.join(app.config['CALENDAR_PATH'], str(slot_id) + '.ics')
    path = os.path.join('app', file_path)
    with open(path, 'w') as f:
        f.writelines(c)
    return file_path


def send_new_booking_email(slot):
    path = create_calendar_file(slot)

    send_email('New booking!',
                sender=app.config['ADMINS'][0],
                recipients=[slot.subject.owner.email, slot.booker.email],
                text_body=render_template('email/new_booking.txt',
                                            slot=slot),
                html_body=render_template('email/new_booking.html',
                                            slot=slot),
                attachment_path=path)

def send_cancellation_email(slot):
    send_email('Booking Cancelled',
            sender=app.config['ADMINS'][0],
            recipients=[slot.subject.owner.email, slot.booker.email],
            text_body=render_template('email/cancellation.txt',
                                        slot=slot),
            html_body=render_template('email/cancellation.html',
                                        slot=slot))

def send_deletion_email(slot):
    send_email('Booking Cancelled',
        sender=app.config['ADMINS'][0],
        recipients=[slot.subject.owner.email, slot.booker.email],
        text_body=render_template('email/deletion.txt',
                                    slot=slot),
        html_body=render_template('email/deletion.html',
                                    slot=slot))