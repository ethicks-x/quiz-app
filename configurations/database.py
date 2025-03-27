from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from flask_migrate import Migrate

# metadata configurations for better labeling
pre_naming = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "pk": "pk_%(table_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s"
}

# database configurations
metadata = MetaData(naming_convention=pre_naming)
db = SQLAlchemy(metadata=metadata)


# creating migration object
def do_migrate(app):
    migrate = Migrate(app, db)
    return migrate


