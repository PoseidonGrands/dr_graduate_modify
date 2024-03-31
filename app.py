from flask import Flask, send_from_directory

from flask_app import conf
from flask_app.accounts.views import accounts
from flask_app.manage.views import manage
from flask_app.model.accounts import db

app = Flask(__name__, template_folder='flask_app/templates', static_folder='flask_app/resources')
# 从配置文件加载配置
app.config.from_object(conf.Config)

# 数据库初始化
db.init_app(app)
with app.app_context():
    db.create_all()


# accounts蓝图注册
app.register_blueprint(accounts, url_prefix='/accounts')
# manage
app.register_blueprint(manage, url_prefix='/')


# 添加src目录为可访问路径
@app.route('/src/features/<path:filename>')
def custom_static(filename):
    return send_from_directory('src', filename)








