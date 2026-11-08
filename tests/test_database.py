from app.database import build_database_url


def test_database_url_defaults_to_local_sqlite(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("DB_HOST", raising=False)
    url = str(build_database_url())
    assert url.startswith("sqlite:///")
    assert url.endswith("tasks.db")


def test_database_url_prefers_explicit_database_url(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://user:pass@db.example/test")
    monkeypatch.setenv("DB_HOST", "ignored.example")
    assert str(build_database_url()) == "postgresql+psycopg://user:pass@db.example/test"


def test_database_url_uses_aws_db_environment(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setenv("DB_HOST", "db.example.internal")
    monkeypatch.setenv("DB_PORT", "5432")
    monkeypatch.setenv("DB_USER", "appuser")
    monkeypatch.setenv("DB_PASSWORD", "p@ss/word")
    monkeypatch.setenv("DB_NAME", "tasks")

    url = build_database_url()
    assert url.drivername == "postgresql+psycopg"
    assert url.host == "db.example.internal"
    assert url.port == 5432
    assert url.username == "appuser"
    assert url.password == "p@ss/word"
    assert url.database == "tasks"
    assert url.query["sslmode"] == "require"
