import os
from collections.abc import Generator
from pathlib import Path

from sqlalchemy import URL, create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


BASE_DIR = Path(__file__).resolve().parent.parent


def build_database_url() -> str | URL:
    """Build a database URL from DATABASE_URL or AWS-injected DB_* variables."""
    configured_url = os.getenv("DATABASE_URL")
    if configured_url:
        return configured_url

    database_host = os.getenv("DB_HOST")
    if database_host:
        return URL.create(
            drivername="postgresql+psycopg",
            username=os.getenv("DB_USER", "taskmanager"),
            password=os.environ["DB_PASSWORD"],
            host=database_host,
            port=int(os.getenv("DB_PORT", "5432")),
            database=os.getenv("DB_NAME", "taskmanager"),
            query={"sslmode": "require"},
        )

    return f"sqlite:///{BASE_DIR / 'tasks.db'}"


DATABASE_URL = build_database_url()
is_sqlite = str(DATABASE_URL).startswith("sqlite")
connect_args = {"check_same_thread": False} if is_sqlite else {}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,
    pool_size=5 if not is_sqlite else 5,
    max_overflow=0 if not is_sqlite else 10,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """Base class for SQLAlchemy database models."""


def get_db() -> Generator[Session, None, None]:
    """Provide a database session and close it after use."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
