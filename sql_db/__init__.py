import os
from argon2 import PasswordHasher
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

sql_db = SQLAlchemy()
migrate = Migrate()

ph = PasswordHasher()

def init_db(app):
    from sql_db.seed import seed_command

    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ["MARIADB_URL"]

    sql_db.init_app(app)
    migrate.init_app(app, sql_db)

    app.cli.add_command(seed_command)



