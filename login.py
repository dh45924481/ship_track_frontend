import datetime
import requests
import time
import threading
import redis

from configs import Redis_ip

from datetime import timedelta
from flask_migrate import Migrate
from exts import db
from configs import *
from flask_cors import CORS
from flask import Response, jsonify, Flask, redirect, url_for, request, flash, session
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy


# 蓝图导入
from Blueprint.Image_blue import imageblue
from Blueprint.user_view import user_view
from Blueprint.commands import cli  # 预置数据导入
from Blueprint.model_view import model_view
from Blueprint.menu_view import menu_view
from Blueprint.model_views import model_views
from Blueprint.scheduler_task import scheduler_task, run_task
from flask_apscheduler import APScheduler
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_babel import Babel
from flask_session import Session
from flask_login import (
    LoginManager,
    login_user,
    login_required,
    logout_user,
    current_user,
)


# --------建立flask实例--------
app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"  # 指定未登录时重定向的视图函数

# --------注册CORS, "/*" 允许访问所有api--------
CORS(app, resources=r"/*")

# --------获取 Flask 应用的根路径--------
root_path = app.root_path

# --------配置密钥--------
app.config["JWT_SECRET_KEY"] = "my_secret_key"

# SQLALCHEMY_TRACK_MODIFICATIONS: 这个选项用于启用或禁用 SQLAlchemy 对象修改的追踪功能。
# True: 启用追踪。当数据库会话中的对象被修改时，SQLAlchemy 会发出信号。这在某些情况下可能会有用，例如，你需要在对象修改时执行某些操作。
# False: 禁用追踪。这是默认的推荐设置。禁用后，可以减少内存开销，因为追踪对象修改需要额外的内存
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


# --------配置 Flask-Session 及login会话--------
# 设置 login-secret_key
app.secret_key = "my_secret_key_login"  # 替换为你的密钥
# 设置会话超时时间为30分钟
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=15)
app.config["SESSION_TYPE"] = "redis"  # 可以使用 'redis', 'filesystem', 'mongodb', 等
app.config["SESSION_PERMANENT"] = True
# 配置 Redis 连接
app.config["SESSION_REDIS"] = redis.Redis(
    host=Redis_ip, port=6379, password=None, db=0
)  # 使用你的 Redis 主机、端口和密码
Session(app)

# --------初始化 JWTManager--------
jwt = JWTManager(app)

# --------过期时间--------
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = 1800

# --------解决中文乱码--------
app.config["JSON_AS_ASCII"] = False


# --------定时任务配置--------
# 配置 APScheduler
class Config_APScheduler:
    SCHEDULER_API_ENABLED = True


app.config.from_object(Config_APScheduler)

# 初始化 APScheduler
scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()

# --------在应用对象上注册蓝图--------
app.register_blueprint(imageblue, url_prefix="/imageblue")
app.register_blueprint(user_view, url_prefix="/user_view")  # 用户蓝图
app.register_blueprint(cli)  # 预置数据蓝图
app.register_blueprint(model_view, url_prefix="/model_view")  # 数据操作蓝图
app.register_blueprint(menu_view, url_prefix="/menu_view")  # 菜单蓝图
app.register_blueprint(model_views, url_prefix="/model_views")  # 新增数据操作蓝图1
app.register_blueprint(scheduler_task, url_prefix="/scheduler_task")  # 定时任务蓝图

# --------连接数据库--------
app.config.from_object(Config)

# --------初始化--------
db.init_app(app)

# --------绑定app和数据库--------
migrate = Migrate(app, db)

# --------后台管理页面 （添加表操作，进行后台管理）--------
babel = Babel(app)
admin = Admin(app, name="My_admin", template_mode="bootstrap3")
admin.add_view(ModelView(Diagnosis_data, db.session))


# 每次接口请求刷新会话时间，如果15分钟内不存在接口请求-退出
@app.before_request
def before_request():
    session.permanent = True  # 刷新会话过期时间
    session.modified = True  # 确保会话被标记为已修改


# 存储userid
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# 登录视图
@app.route("/login", methods=["GET"])
def login():
    username = request.args.get("username")
    password = request.args.get("password")
    user = db.session.query(User).filter(User.username == username).first()
    if user:
        login_user(user)
        return jsonify({"message": "登录成功", "user_id": user.id}), 200
    else:
        return jsonify({"message": "无效用户名或者密码"}), 401


# 受保护的视图
@app.route("/protected")
@login_required
def protected():
    return jsonify({"message": f"Hello, {current_user.username}!"}), 200


# 注销视图
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return jsonify({"message": "用户注销成功"}), 200


# --------调用实例对象--------
if __name__ == "__main__":
    # setup_scheduler_tasks()
    app.run(debug=False, host="0.0.0.0", port=5000)
