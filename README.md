
conda create -n flask python=3.10

conda activate flask

pip install Flask-Migrate==4.0.7 -i https://mirrors.aliyun.com/pypi/simple/

pip install mysql-connector-python==9.1.0  -i https://mirrors.aliyun.com/pypi/simple/

pip install Flask-Login==0.6.3  -i https://mirrors.aliyun.com/pypi/simple/

pip install pymysql -i https://mirrors.aliyun.com/pypi/simple/

flask run 启动程序

127.0.0.1:5000打开网页

pip install -r requirements.txt

config.py配置中的SQLALCHEMY_DATABASE_URI修改为自己的数据库连接配置

运行db.create_all()，根据SQLAlchemy模型创建数据库表。

4.运行Role.insert_roles()，初始化用户角色。

5.u = models.User(username='xxx', password='xxx')
  db.session.add(u)

  用来创建用户，用户信息保存在mysql数据库中。
