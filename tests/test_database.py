from sqlalchemy.engine import make_url

from app.database import build_database_url, get_db, render_database_url


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


def test_database_url_prefers_explicit_database_url(monkeypatch):
    configured_url = "postgresql+psycopg://user:password@db.example.com/tasks"

    monkeypatch.setenv("DATABASE_URL", configured_url)
    monkeypatch.setenv("DB_HOST", "another-host")

    assert build_database_url() == configured_url


def test_get_db_closes_session_after_use(monkeypatch):
    class FakeSession:
        closed = False

        def close(self):
            self.closed = True

    fake_session = FakeSession()

    monkeypatch.setattr(
        "app.database.SessionLocal",
        lambda: fake_session,
    )

    generator = get_db()

    session = next(generator)

    assert session is fake_session
    assert fake_session.closed is False

    generator.close()

    assert fake_session.closed is True
