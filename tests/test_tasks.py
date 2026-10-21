
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db


@pytest.fixture
def client():
    test_engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=test_engine,
    )

    Base.metadata.create_all(bind=test_engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()
        Base.metadata.drop_all(bind=test_engine)
        test_engine.dispose()


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_task(client):
    response = client.post(
        "/tasks/",
        json={
            "title": "Learn DevSecOps",
            "description": "Build a secure API",
            "completed": False,
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Learn DevSecOps"
    assert data["completed"] is False
    assert "id" in data


def test_list_tasks(client):
    create_response = client.post(
        "/tasks/",
        json={"title": "Task to list"},
    )
    assert create_response.status_code == 201

    response = client.get("/tasks/")

    assert response.status_code == 200
    assert any(
        task["title"] == "Task to list"
        for task in response.json()
    )


def test_missing_task_returns_404(client):
    response = client.get("/tasks/999999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"


def test_blank_title_is_rejected(client):
    response = client.post(
        "/tasks/",
        json={"title": "   "},
    )
    assert response.status_code == 422

def test_update_task(client):
    create_response = client.post(
        "/tasks/",
        json={"title": "Original task"},
    )
    assert create_response.status_code == 201

    task_id = create_response.json()["id"]

    response = client.put(
        f"/tasks/{task_id}",
        json={
            "title": "Updated task",
            "completed": True,
        },
    )

    assert response.status_code == 200
    assert response.json()["title"] == "Updated task"
    assert response.json()["completed"] is True


def test_delete_task(client):
    create_response = client.post(
        "/tasks/",
        json={"title": "Task to delete"},
    )
    assert create_response.status_code == 201

    task_id = create_response.json()["id"]

    response = client.delete(f"/tasks/{task_id}")
    assert response.status_code == 204

    get_response = client.get(f"/tasks/{task_id}")
    assert get_response.status_code == 404
