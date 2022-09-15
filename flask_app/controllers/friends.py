from flask import Flask, render_template, redirect, session, request, flash
from flask_app.models import user, friend
from flask_app import app

@app.route('/friendships')
def r_friendships():
    print('loading friendships page...')

    return render_template('friendships.html')