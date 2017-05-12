#-*-coding:utf-8-*-
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import Regexp

class LoginForm(FlaskForm):
    username = StringField()
    password = PasswordField()
    submit = SubmitField()