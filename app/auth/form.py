#-*-coding:utf-8-*-
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import Regexp

class LoginForm(FlaskForm):
    username = StringField(validators=[Regexp('^1[3|5|7|8][0-9]{9}$',0,'phone error')])
    password = PasswordField()
    submit = SubmitField()