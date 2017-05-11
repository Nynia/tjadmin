# -*-coding:utf-8-*-
from flask_wtf import FlaskForm
from wtforms import SubmitField, FileField, StringField, SelectField,TextAreaField
from flask_wtf.file import FileAllowed, FileRequired,DataRequired


class UploadForm(FlaskForm):
    blackfile = FileField(u'黑名单文件', validators=[FileRequired(), FileAllowed(['txt'], 'Text only!')])
    type = SelectField(u'类型',choices=[
        ('black',u'黑名单'),('red',u'红名单')])
    remark = StringField(u'备注')
    submit = SubmitField(u'提交')

class SingleAddForm(FlaskForm):
    number = TextAreaField(u'号码',validators=[DataRequired()])
    type = SelectField(u'类型',choices=[
        ('black',u'黑名单'),('red',u'红名单')])
    remark = StringField(u'备注')
    submit = SubmitField(u'提交')

class FilterForm(FlaskForm):
    sourcefile = FileField(u'源文件', validators=[FileRequired(), FileAllowed(['txt'], 'Text only!')])
    submit = SubmitField(u'过滤并下载到本地')