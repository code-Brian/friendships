from flask import Flask, render_template, redirect, session, request, flash
from flask_app.models import user, friend
from flask_app import app

@app.route('/friendships')
def r_friendships():
    print('loading friendships page...')
    friendships=user.User.get_all_friendships()
    created = friend.Friend.get_friendship_created()
    users = user.User.get_all()

    return render_template('friendships.html', friendships=friendships, created=created, users=users)

@app.route('/user/add', methods=['POST'])
def f_user_add():
    parse = user.User.parse_user_data(request.form)
    print(parse)

    if not user.User.validate_new_user(parse):
        session['new_user_fname'] = parse['first_name']
        session['new_user_lname'] = parse['last_name']

        return redirect('/friendships')
    
    session.pop('new_user_fname', None)
    session.pop('new_user_lname', None)

    user.User.user_add(parse)

    return redirect('/friendships')

@app.route('/friend/add', methods=['POST'])
def f_friend_add():

    data = {
        'user_id' : int(request.form.get('user_id')),
        'friend_id' : int(request.form.get('friend_id'))
    }

    print(f"printing add friend data {data}.................................................")

    friend.Friend.add_friendship(data)

    return redirect('/friendships') 