from app import app
from flask import render_template, flash, redirect
from app.forms import LoginForm, RegisterForm
import os
import json

@app.route('/')
@app.route('/index')
def index():
    user = {'username': 'Dog User'}
    return render_template('index.html', title='Home', user=user)

# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     form = LoginForm()
#     if form.validate_on_submit():
#         flash('Login requested for user {}, remember_me={}'.format(
#             form.username.data, form.remember_me.data))
#         return redirect('/index')
#     return render_template('login.html', title='Sign In', form=form)

def save_down_dog(form):
    """Given form, save down data as json"""

    # make a dict to save info and save down as json
    data = {'dog_name': str(form.dogname.data),
            'owner': str(form.personname.data),
            'phone': str(form.phone.data),
            'email': str(form.email.data)}
    # import pdb; pdb.set_trace()
    data_dir = os.environ['DATA_DIR']
    file_path = os.path.join(data_dir, str(form.email.data) + '.json')
    with open(file_path, 'wt') as outfile:
        json.dump(data, outfile)


@app.route('/register_dog', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        # flash('Login requested for user {}, remember_me={}'.format(
            # form.username.data, form.remember_me.data))

        # Save down new dog info to AWS
        save_down_dog(form)
        flash('Dog Registered: {}'.format(form.dogname.data))
        return redirect('/index')
    return render_template('register_dog.html', title='Register Dog', form=form)

def load_available_dogs():
    data_dir = os.environ['DATA_DIR']
    dogs = os.listdir(data_dir)
    res = []
    for fname in dogs:
        path = os.path.join(data_dir, fname)
        with open(path) as json_file:
            data = json.load(json_file)
            res.append(data)
    return res


@app.route('/')
@app.route('/view_dogs')
def view_dogs():
    dogs = load_available_dogs()
    return render_template('view_dogs.html', title='View Dogs', dogs=dogs)