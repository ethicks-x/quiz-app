from app import app
from flask_login import LoginManager, current_user

from configurations.database import db
from models.model import User


user_entrance = LoginManager()
user_entrance.init_app(app)
user_entrance.login_view = "auth.login"


@user_entrance.user_loader
def load_user(user_id):
    return db.session.get(User, user_id)


@user_entrance.unauthorized_handler
def unauthorized_handler():
    return 'Unauthorized', 401


