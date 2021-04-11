from flask_mail import Message
from app import mail
from app import app
from flask import render_template
from threading import Thread
import os
from ics import Calendar, Event
import datetime

from flask import url_for


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
    
    # Site times are in local time. Calendar ics files in UTC. 
    # During BST that means a 10AM slot start would appear as 11AM in BST
    # Therefore necessary to convert to local time
    # TODO this is a quick hack. Fix properly!
    first_val_start = start.split(':')[0]
    start = str(int(first_val_start) - 1) + ':' + start.split(':')[1]

    first_val_end = end.split(':')[0]
    end = str(int(first_val_end) - 1) + ':' + end.split(':')[1]

    # check if start in correct format
    first_val = start.split(':')[0]
    if len(first_val) == 1:
        start = '0' + start

    # check if end in correct format
    first_val = end.split(':')[0]
    if len(first_val) == 1:
        end = '0' + end

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

def send_new_blast(slot):
    """New blast created. Recipients and blaster must receive a message"""
    blaster_email = slot.subject.owner.email
    
    send_new_blast_blaster(slot)

    for blast in slot.blasts:
        link = url_for('view_blast', blast_id=blast.id, _external=True)
        recipient_email = blast.blast_receiver.email
        send_blast_individual(recipient_email, blast, link)

def send_blast_individual(recipient_email, blast, link):
    """Send email to recipient of Dog Blast to notify of new dog blast."""
    send_email('New Dog Blast Received',
    sender=app.config['ADMINS'][0],
    recipients=[recipient_email],
    text_body=render_template('email/new_blast.html', blast=blast,
                                slot=blast.slot, link=link),
    html_body=render_template('email/new_blast.html', blast=blast,
                                slot=blast.slot, link=link))

def send_withdrawn_blast_individual(recipient_email, blast):
    """Send email to recipient of Dog Blast to notify of withdrawn dog blast."""
    send_email('Dog Blast Cancelled!',
    sender=app.config['ADMINS'][0],
    recipients=[recipient_email],
    text_body=render_template('email/withdrawn_blast.html', blast=blast,
                                slot=blast.slot),
    html_body=render_template('email/withdrawn_blast.html', blast=blast,
                                slot=blast.slot))

def send_blast_fulfilled_individual(recipient_email, blast):
    """Send email to recipient of Dog Blast to notify of fulfilled dog blast by other user."""
    send_email('Dog Blast Fulfilled',
    sender=app.config['ADMINS'][0],
    recipients=[recipient_email],
    text_body=render_template('email/fulfilled_blast.txt', blast=blast,
                                slot=blast.slot),
    html_body=render_template('email/fulfilled_blast.html', blast=blast,
                                slot=blast.slot))

def send_new_blast_blaster(slot):
    """Notify blaster of their new blast"""
    blaster_email = slot.subject.owner.email
    link = url_for('my_blast', slot_id=slot.id, _external=True)
    send_email('Dog Blast created',
    sender=app.config['ADMINS'][0],
    recipients=[blaster_email],
    text_body=render_template('email/blast_details.txt',
                                slot=slot, link=link),
    html_body=render_template('email/blast_details.html',
                                slot=slot, link=link))

def send_rejected_blast(blast):
    """User rejects a blast_received. Email received by blaster."""
    blaster_email = blast.slot.subject.owner.email
    link = url_for('my_blast', slot_id=blast.slot.id, _external=True)
    send_email('Dog Blast rejected',
    sender=app.config['ADMINS'][0],
    recipients=[blaster_email],
    text_body=render_template('email/reject_blast.txt', blast=blast,
                                slot=blast.slot, link=link),
    html_body=render_template('email/reject_blast.html', blast=blast,
                                slot=blast.slot, link=link))

def send_accepted_blast(blast):
    """User accepts a blast_received. Email received by blaster and receiver."""
    blaster_email = blast.slot.subject.owner.email
    link = url_for('my_blast', slot_id=blast.slot.id, _external=True)
    send_email('Dog Blast accepted!',
    sender=app.config['ADMINS'][0],
    recipients=[blaster_email, blast.blast_receiver.email],
    text_body=render_template('email/accept_blast.txt', blast=blast,
                                slot=blast.slot, link=link),
    html_body=render_template('email/accept_blast.html', blast=blast,
                                slot=blast.slot, link=link))

def send_withdrawn_blast(slot):
    # blaster_email = slot.subject.owner.email

    for blast in slot.blasts:
        if blast.status != 'REJECTED':
            recipient_email = blast.blast_receiver.email
            send_withdrawn_blast_individual(recipient_email, blast)


def send_blast_fulfilled_email(slot):    
    for blast in slot.blasts:
        # Don't send email mentioning fufilled to booker
        if blast.slot.booker.id == blast.receiver:
            continue
        recipient_email = blast.blast_receiver.email
        send_blast_fulfilled_individual(recipient_email, blast)
