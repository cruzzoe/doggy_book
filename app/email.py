from flask_mail import Message
from app import mail
from app import app
from flask import render_template
from threading import Thread

def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

def send_email(subject, sender, recipients, text_body, html_body):
    if not app.debug:
        msg = Message(subject, sender=sender, recipients=recipients)
        msg.body = text_body
        msg.html = html_body
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

def send_new_booking_email(slot):
    send_email('New booking!',
               sender=app.config['ADMINS'][0],
               recipients=[slot.subject.owner.email, slot.booker.email],
               text_body=render_template('email/new_booking.txt',
                                         slot=slot),
               html_body=render_template('email/new_booking.html',
                                         slot=slot))

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