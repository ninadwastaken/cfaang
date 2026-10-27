from sql_db import sql_db

class User(sql_db.Model):
    __tablename__ = "users"

    id = sql_db.Column(sql_db.Integer, primary_key=True)
    username = sql_db.Column(sql_db.String(32), unique=True, nullable=False)