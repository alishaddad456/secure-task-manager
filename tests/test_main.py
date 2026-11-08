from sqlalchemy.exc import SQLAlchemyError


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_readiness_check(client, monkeypatch):
    class FakeConnection:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def execute(self, statement):
            return 1

    monkeypatch.setattr("app.main.engine.connect", lambda: FakeConnection())
    response = client.get("/ready")
    assert response.status_code == 200
    assert response.json() == {"status": "ready"}


def test_readiness_check_returns_503_when_database_is_unavailable(client, monkeypatch):
    def fail_connection():
        raise SQLAlchemyError("database unavailable")

    monkeypatch.setattr("app.main.engine.connect", fail_connection)
    response = client.get("/ready")
    assert response.status_code == 503
    assert response.json() == {
        "status": "not_ready",
        "dependency": "database",
    }
