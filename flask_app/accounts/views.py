from flask import render_template, redirect, url_for, Blueprint, flash

from flask_app.accounts.form import RegisterForm, LoginForm
from flask_app.model.accounts import User, db

accounts = Blueprint('accounts', __name__, template_folder='templates', static_folder='resources/static')


@accounts.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()

    # 表单验证（没有这条判断则内置或自定义表单验证不起作用
    if form.validate_on_submit():
        # 1、获取表单信息
        email = form.email.data
        nickname = form.nickname.data
        password = form.password.data

        # 2、构建用户对象
        user = User(email=email, nickname=nickname, password=password)

        # 3、保存到数据库
        db.session.add(user)
        db.session.commit()

        # 4、跳转到登录页面
        return redirect(url_for('accounts.login'))

    return render_template('register.html', form=form)


@accounts.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    # 不加csrftoken即使输入的没问题也过不了验证，因为默认开了csrf保护
    if form.validate_on_submit():
        # 1、获取表单数据
        email = form.email.data
        password = form.password.data

        # 2、查询密码是否正确
        user = User.query.filter_by(email=email).first()
        if password == user.password:
            # flash('登录成功, 正在跳转', 'success')
            # 跳转页面
            return redirect('/0')
        else:
            flash('密码错误', 'danger')

        # 3、跳转到后台管理页面

    return render_template('login.html', form=form)



