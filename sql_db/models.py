from sql_db import sql_db
from datetime import datetime, timezone

# standard tables
class Users(sql_db.Model):
    __tablename__ = "users"

    uid = sql_db.Column(sql_db.Integer, primary_key=True)
    username = sql_db.Column(sql_db.String(32), unique=True, nullable=False)
    password = sql_db.Column(sql_db.String(255), nullable=False) # stored as argon2 hash, plaintext password must never be stored in the database!

class Groups(sql_db.Model):
    __tablename__ = "groups"

    gid = sql_db.Column(sql_db.Integer, primary_key=True)
    group_name = sql_db.Column(sql_db.String(32), unique=True, nullable=False)

class Endpoints(sql_db.Model):
    __tablename__ = "endpoints"

    epid = sql_db.Column(sql_db.Integer, primary_key=True)
    endpoint_name = sql_db.Column(sql_db.String(32), unique=True, nullable=False)

class Permissions(sql_db.Model):
    __tablename__ = "permissions"

    pmid = sql_db.Column(sql_db.Integer, primary_key=True)
    epid = sql_db.Column(sql_db.Integer, sql_db.ForeignKey("endpoints.epid"), nullable=False)
    permission_name = sql_db.Column(sql_db.String(256), nullable=False)
    # mask is a 4 bit binary value ranging from 0 to 15.
    # each bit corresponds to CRUD respectively.
    # for example, 0100 only allows read, 1011 allows everything except update, etc.
    # also, important to note permissions follow deny by default
    mask = sql_db.Column(sql_db.Integer, sql_db.CheckConstraint("mask BETWEEN 0 AND 15"), nullable=False)

class ApiTokens(sql_db.Model):
    __tablename__ = "api_tokens"

    tid = sql_db.Column(sql_db.Integer, primary_key=True)
    uid = sql_db.Column(sql_db.Integer, sql_db.ForeignKey("users.uid"), nullable=False)
    token_hash = sql_db.Column(sql_db.String(64), index=True, unique=True, nullable=False) # stored as sha256 hash, plaintext token must never be stored in the database!
    created_at = sql_db.Column(sql_db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    expires_at = sql_db.Column(sql_db.DateTime(timezone=True), nullable=False)
    revoked_at = sql_db.Column(sql_db.DateTime(timezone=True), nullable=True, default=None)

# associative tables
class GroupUsers(sql_db.Model):
    __tablename__ = "group_users"

    gid = sql_db.Column(sql_db.Integer, sql_db.ForeignKey("groups.gid"), primary_key=True)
    uid = sql_db.Column(sql_db.Integer, sql_db.ForeignKey("users.uid"), primary_key=True)

class GroupPermissions(sql_db.Model):
    __tablename__ = "group_permissions"

    gid = sql_db.Column(sql_db.Integer, sql_db.ForeignKey("groups.gid"), primary_key=True)
    pmid = sql_db.Column(sql_db.Integer, sql_db.ForeignKey("permissions.pmid"), primary_key=True)
