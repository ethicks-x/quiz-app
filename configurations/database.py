from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from flask_migrate import Migrate

# metadata configurations for better labeling
pre_naming = {
    "ix": "_ix_%(column_0_label)_",
    "uq": "_uq_%(table_name)_%(column_0_name)_",
    "pk": "_pk_%(table_name)_",
    "ck": "_ck_%(table_name)_%(constraint_name)_",
    "fk": "_fk_%(table_name)_%(column_0_name)_%(referred_table_name)_"
}

# database configurations
metadata = MetaData(naming_convention=pre_naming)
db = SQLAlchemy(metadata=metadata)


# creating migration object
def do_migrate(app):
    migrate = Migrate(app, db)
    return migrate


