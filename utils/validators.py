import re

from wtforms import ValidationError

from flask_app.model.accounts import User


def validate_password(self, field):
    """验证密码，需要大于等于八位并且需要包含大小写字母、数字和特殊字符"""
    password = field.data
    if len(password) < 2:
        raise ValidationError('密码长度需大于7位')

    """
        密码格式检查
        长度要求：密码的长度通常要求在一定的范围之内，比如6到16个字符之间。
        字符类型要求：密码通常需要包含至少一个大写字母、一个小写字母、一个数字和一个特殊字符。
        
        ^：匹配字符串的开始位置。
        (?=.*[a-z])：使用正向预查，表示必须包含至少一个小写字母。
        (?=.*[A-Z])：使用正向预查，表示必须包含至少一个大写字母。
        (?=.*\d)：使用正向预查，表示必须包含至少一个数字。
        (?=.*[@$!%*?&.])：使用正向预查，表示必须包含至少一个特殊字符。
        [A-Za-z\d@$!%*?&.]{6,16}：匹配包含大小写字母、数字和特殊字符的字符串，并且长度在6到16个字符之间。
        $：匹配字符串的结束位置。
    """
    pattern = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&.])[A-Za-z\d@$!%*?&.]{6,16}$"
    if not re.search(pattern, password):
        raise ValidationError('密码需要包含大小写字母、数字和特殊字符')


def validate_email(self, field):
    """验证此邮箱是否被注册"""
    if User.query.filter_by(email=field.data).first():
        raise ValidationError('此邮箱已经被注册')


def validate_nickname(self, field):
    """验证此昵称是否被占用"""
    if User.query.filter_by(nickname=field.data).first():
        raise ValidationError('此昵称已经被占用')


def validate_email_login(self, field):
    """验证邮箱是否存在"""
    if not User.query.filter_by(email=field.data).first():
        raise ValidationError('此邮箱未注册')


