#-*-coding:utf-8-*-
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import Regexp

class LoginForm(FlaskForm):
    username = StringField(u'帐 号')
    password = PasswordField(u'密 码')
    submit = SubmitField(u'登  录')