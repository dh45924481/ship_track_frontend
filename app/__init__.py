# coding=utf-8

import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

app = Flask(__name__,static_folder='main/static',static_url_path='/static')
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:123456@127.0.0.1:3306/test?charset=utf8'  # 根据你的配置调整
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config.from_object('config')
db = SQLAlchemy(app)

login_manager=LoginManager()
login_manager.session_protection='strong'
login_manager.login_view='main.login'
# login_manager.login_message = "Bonvolu ensaluti por uzi tio paĝo."
login_manager.init_app(app)

from .main import main as main_blueprint
app.register_blueprint(main_blueprint)

from .auth import auth as auth_blueprint
app.register_blueprint(auth_blueprint)

# from app import views, models