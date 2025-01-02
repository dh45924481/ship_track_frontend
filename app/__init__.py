# coding=utf-8

import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import pytz

app = Flask(__name__, static_folder="main/static", static_url_path="/static")
app.config["SQLALCHEMY_DATABASE_URI"] = (
    "mysql+mysqlconnector://root:hasf12345@47.116.5.151:13316/jiance?charset=utf8&connect_timeout=30&read_timeout=60&write_timeout=60"  # 根据你的配置调整
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_POOL_SIZE"] = 3  # 减少连接池大小
app.config["SQLALCHEMY_POOL_TIMEOUT"] = 10  # 减少超时时间
app.config["SQLALCHEMY_POOL_RECYCLE"] = 60  # 减少连接回收时间到1分钟
app.config["SQLALCHEMY_MAX_OVERFLOW"] = 1  # 减少最大溢出连接数
app.config["SQLALCHEMY_POOL_PRE_PING"] = True  # 启用连接池预检
app.config["TIMEZONE"] = pytz.timezone("Asia/Shanghai")  # 设置时区为中国标准时间
app.config.from_object("config")
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.session_protection = "strong"
login_manager.login_view = "auth.login"
# login_manager.login_message = "Bonvolu ensaluti por uzi tio paĝo."
login_manager.init_app(app)

from .main import main as main_blueprint

app.register_blueprint(main_blueprint)

from .auth import auth as auth_blueprint

app.register_blueprint(auth_blueprint)

# from app import views, models
