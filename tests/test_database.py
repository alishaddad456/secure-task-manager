from sqlalchemy.engine import make_url

from app.database import build_database_url, render_database_url


def test_database_url_defaults_to_local_sqlite(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("DB_HOST", raising=False)
    url = str(build_database_url())
    assert url.startswith("sqlite:///")
    assert url.endswith("tasks.db")


def test_database_url_uses_postgres_environment(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setenv("DB_HOST", "db.example.internal")
    monkeypatch.setenv("DB_USER", "appuser")
    monkeypatch.setenv("DB_PASSWORD", "p@ss/word")
    monkeypatch.setenv("DB_NAME", "tasks")
    url = build_database_url()
    assert url.drivername == "postgresql+psycopg"
    assert url.host == "db.example.internal"
    assert url.username == "appuser"
    assert url.password == "p@ss/word"
    assert url.database == "tasks"
    assert url.query["sslmode"] == "require"


def test_render_database_url_keeps_the_real_password(monkeypatch):
    """Regression: str(URL) masks the password as ***, which broke Alembic."""
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setenv("DB_HOST", "db.example.internal")
    monkeypatch.setenv("DB_USER", "appuser")
    monkeypatch.setenv("DB_PASSWORD", "p@ss/word")
    rendered = render_database_url()
    assert "***" not in rendered
    assert make_url(rendered).password == "p@ss/word"


def test_render_database_url_returns_sqlite_string(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("DB_HOST", raising=False)
    assert render_database_url().startswith("sqlite:///")
