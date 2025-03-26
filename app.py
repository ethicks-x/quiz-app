from flask import Flask
from flask_migrate import Migrate 
from flask_bootstrap import Bootstrap5
from dotenv import dotenv_values

from configurations import config
from configurations.database import db, do_migrate
from configurations.config import LocalDevConfig

from controllers.normal import *

env = dotenv_values(".env")
app = None

def create_app():
    app = Flask(__name__, template_folder="templates/")
    app.config.from_object(LocalDevConfig)

    db.init_app(app)
    
    do_migrate(app)
    
    with app.app_context():
        db.create_all()

    return app


app = create_app()

if __name__ == '__main__':
    app.run(
        host=env["HOST"],
        port=env["PORT"]
    )
