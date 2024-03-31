import re

from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, FileField
from wtforms.validators import DataRequired, ValidationError, Length, Email, EqualTo

from utils.validators import validate_password, validate_nickname, validate_email, validate_email_login


class RegisterForm(FlaskForm):
    email = StringField(label='注册邮箱', render_kw={
        'class': 'form-control',
        'placeholder': '邮箱地址',
    }, validators=[DataRequired('请输入邮箱地址'),
                   Email(),
                   validate_email])
    nickname = StringField(label='昵称', render_kw={
        'class': 'form-control',
        'placeholder': '昵称',
    }, validators=[DataRequired('请输入昵称'),
                   Length(min=2, max=20, message='昵称长度在2至20字符'),
                   validate_nickname])
    password = PasswordField(label='密码', render_kw={
        'class': 'form-control',
        'placeholder': '密码',
    }, validators=[DataRequired('请输入密码'),
                   validate_password])
    confirm_password = PasswordField(label='确认密码', render_kw={
        'class': 'form-control',
        'placeholder': '确认密码',
    }, validators=[DataRequired('请输入确认密码'),
                   EqualTo('password', message='两次输入的密码不匹配')])
    submit = SubmitField('注册', render_kw={
        'class': 'btn btn-primary btn-block mt-2',
        'placeholder': '注册账号',
    })


class LoginForm(FlaskForm):
    """登录表单"""
    email = StringField(label='邮箱', render_kw={
        'class': 'form-control',
        'placeholder': '邮箱地址',
    }, validators=[DataRequired('请输入邮箱地址'),
                   Email(),
                   validate_email_login])

    password = PasswordField(label='密码', render_kw={
        'class': 'form-control',
        'placeholder': '密码',
    }, validators=[DataRequired('请输入密码')])

    submit = SubmitField('登录', render_kw={
        'class': 'btn btn-primary btn-block mt-2'
    })
