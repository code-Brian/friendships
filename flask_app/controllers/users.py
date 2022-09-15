from flask import Flask, render_template, redirect, session, request, flash
from flask_app.models import user
from flask_app import app
from flask_bcrypt import Bcrypt

BCRYPT = Bcrypt(app)

@app.route('/')
def r_login():
    print('rendering login page...')

    return render_template('login.html')

@app.route('/user/register', methods=['POST'])
def f_user_register():
    # parse incoming form data
    parsed = user.User.parse_user_registration(request.form)

    print("Parsed data was:",parsed)

    # validate incoming form data
    if not user.User.validate_registration(request.form):
        session['first_name'] = request.form.get('first_name')
        session['last_name'] = request.form.get('last_name')
        session['register_email'] = request.form.get('email')
        return redirect('/')

    # once formdata is validated, clear the session
    session.clear()

    # save a new user into database
    user_id = user.User.save(parsed)
    print(user_id)

    # assign the session user id to the newly registered user id
    session['user_id'] = user_id

    return redirect('/friendships')

@app.route('/user/login', methods=['POST'])
def f_user_login():
    print('Attempting to login...')

    data = {
        'email' : request.form.get('email')
    }

    user_match = user.User.get_user_by_email(data)

    if not user_match:
        flash(u'Invalid Email/Password', 'login')
        return redirect('/')
    
    if not BCRYPT.check_password_hash(user_match.password, request.form.get('password')):
        flash(u'Invalid Email/Password', 'login')
        return redirect('/')

    session['user_id'] = user_match.id
    session['first_name'] = user_match.first_name.capitalize()
    session['last_name'] = user_match.last_name.capitalize()

    return redirect('/friendships')

@app.route('/logout')
def d_logout():
    print('clearing the session and logging out')
    session.clear()
    return redirect('/')