import states.query as qry


def test_query(monkeypatch):
    monkeypatch.setattr(qry, 'is_db_up', lambda: True)
    states = qry.get_states()
    assert isinstance(states, dict)


def test_query_when_database_is_down(monkeypatch):
    monkeypatch.setattr(qry, 'is_db_up', lambda: False)
    assert qry.get_states() is None
