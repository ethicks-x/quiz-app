from flask import Flask
from dotenv import load_dotenv, dotenv_values

from configurations.config import LocalDevConfig

app = None


def create_app():
    app = Flask(__name__, template_folder="templates/")
    env = dotenv_values(".env")
    app.config.from_object(LocalDevConfig)
    app.app_context.push()

    return app


app = create_app()

