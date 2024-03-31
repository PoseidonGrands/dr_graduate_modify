import os


class Config(object):
    # 数据库连接参数
    HOSTNAME = 'localhost'
    PORT = 3306
    USERNAME = 'root'
    PASSWORD = '2280139492'
    DATABASE = 'dr_weibo'

    # 数据库配置
    SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{USERNAME}:{PASSWORD}@{HOSTNAME}:{PORT}/{DATABASE}?charset=utf8mb4'
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    # secret key
    WTF_CSRF_SECRET_KEY = '25IGoAK1g2aJUky9CXx5L8H2LXnUNB7M'
    SECRET_KEY = '25IGoAK1g2aJUky9CXx5L8H2LXnUNB7M'

    # 文件上传的路径
    UPLOAD_PATH = os.path.join(os.path.dirname(__file__), 'resources')
