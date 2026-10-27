import os

os.environ.setdefault(
    "MARIADB_URL",
    "mysql+pymysql://admin:admin@localhost:3306/cfaang",
)

from unittest.mock import MagicMock

import pytest
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from sql_db import sql_db
from server.endpoints import app

def test_is_db_up_pings_mariadb(monkeypatch):
    execute = MagicMock()
    monkeypatch.setattr(sql_db.session, "execute", execute)

    with app.app_context():
        assert is_db_up() is True
        execute.assert_called_once()
        assert str(execute.call_args.args[0]) == "SELECT 1"

def test_is_db_up_returns_false_when_query_fails(monkeypatch):
    execute = MagicMock(side_effect=SQLAlchemyError("Database unavailable"))
    monkeypatch.setattr(sql_db.session, "execute", execute)

    with app.app_context():
        assert is_db_up() is False
        execute.assert_called_once()
        assert str(execute.call_args.args[0]) == "SELECT 1"

def is_db_up():
    try:
        sql_db.session.execute(text("SELECT 1"))
        return True
    except SQLAlchemyError:
        return False
