import os 
from flask_bcrypt import Bcrypt

db_path = os.path.join(os.path.abspath(os.getcwd()), './database_dir')
os.makedirs(db_path, exist_ok=True)

bcrypt = Bcrypt()

class Config():
    DEBUG = False
    SQLITE_DB_DIR = None
    SQLALCHEMY_DATABASE_URI = None
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    BCRYPT = bcrypt


class LocalDevConfig(Config):
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(os.path.abspath(os.getcwd()), './database_dir/database.db')
    DEBUG = True 