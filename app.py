from flask import Flask
from flask_migrate import Migrate 
from flask_bootstrap import Bootstrap5
from dotenv import dotenv_values

from configurations import config
from configurations.database import db, do_migrate
from configurations.config import LocalDevConfig

import models.model

env = dotenv_values(".env")

app = Flask(__name__, template_folder="templates/")
app.config.from_object(LocalDevConfig)
app.secret_key = env["SECRET_KEY"]

bootstrap = Bootstrap5(app)

db.init_app(app)
do_migrate(app)

with app.app_context():
    db.create_all()

from controllers.normal import *

from configurations.loginManager import *

from routes import auth

# app.register_blueprint(auth.auth)

if __name__ == '__main__':
    app.run(
        host=env["HOST"],
        port=env["PORT"]
    )
