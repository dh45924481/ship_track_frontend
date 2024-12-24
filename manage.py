from flask import Flask
from flask_migrate import Migrate
from app import app, db
from app.models import Role, User

# 初始化 Migrate
migrate = Migrate(app, db)

# 使用 Flask 自带的 CLI 功能
@app.cli.command("init-db")
def init_db():
    """Initialize the database."""
    with app.app_context():
        db.create_all()
        Role.insert_roles()
        print("Initialized the database and inserted roles.")

@app.cli.command("drop-db")
def drop_db():
    """Drop the database."""
    with app.app_context():
        db.drop_all()
        print("Dropped the database.")

@app.cli.command("create-admin")
def create_admin():
    """Create an admin user."""
    with app.app_context():
        admin = User(username='admin', email='admin@example.com', is_admin=True)
        db.session.add(admin)
        db.session.commit()
        print("Admin user created.")

@app.cli.command("create-user")
def create_user():
    """Create a new user."""
    with app.app_context():
        username = input("Enter username: ")
        password = input("Enter password: ")
        user = User(username=username)
        user.password = password
        db.session.add(user)
        db.session.commit()
        print(f"User {username} created.")

if __name__ == '__main__':
    app.run()