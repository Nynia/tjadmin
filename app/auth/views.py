# -*-coding=utf-8-*-
from . import auth
from flask_login import login_user
from flask import render_template, redirect, url_for, flash
from .form import LoginForm
from app.models import BlACKUSER


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = BlACKUSER.query.filter_by(username=form.username.data).first()
        print user
        print form.username.data
        if user is not None and user.verify_password(form.password.data):
            login_user(user)
            return redirect(url_for('main.admin'))
        print 'password error'
        form.username.data = ''
        form.password.data = ''
    return render_template('login.html', form=form)
