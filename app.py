from flask import Flask, send_from_directory, redirect, url_for
from flask_bootstrap import Bootstrap5
from flask_login import current_user, LoginManager
from dotenv import dotenv_values
from models.model import User
import os

from configurations.database import db, do_migrate
from configurations.config import LocalDevConfig

env = dotenv_values(".env")

# Initialize Flask app
app = Flask(__name__, template_folder="templates/")
app.config.from_object(LocalDevConfig)
app.secret_key = env["SECRET_KEY"]

db.init_app(app)
do_migrate(app)

bootstrap = Bootstrap5(app)

with app.app_context():
    db.create_all()

user_entrance = LoginManager()
user_entrance.init_app(app)
user_entrance.login_view = "auth.login"

@user_entrance.user_loader
def load_user(user_id):
    return db.session.get(User, user_id)
    # return User.query.get(int(user_id))

@user_entrance.unauthorized_handler
def unauthorized_handler():
    return 'Unauthorized', 401

from routes import auth, admin, user
app.register_blueprint(user.user_bp)
app.register_blueprint(admin.admin_bp)
app.register_blueprint(auth.auth)


@app.route('/')
def home():
    if current_user.is_authenticated:
        # Check if user is admin
        if current_user.role == "admin":
            return redirect(url_for("admin.quizes"))
        else:
            return redirect(url_for("user.dashboard"))

    return redirect(url_for("auth.login"))


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static/images'), 'favicon.ico')


if __name__ == '__main__':
    app.run(
        host=env["HOST"],
        port=env["PORT"]
    )
