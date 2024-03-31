from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    """ 用户模型 """
    __tablename__ = 'accounts_user'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 主键
    # 邮箱，用于登录
    email = db.Column(db.String(256), unique=True, nullable=False)
    # 用户昵称
    nickname = db.Column(db.String(64))
    password = db.Column(db.String(256), nullable=False)


