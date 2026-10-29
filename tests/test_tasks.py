def create_task(client, title="Test task", description=None):
    return client.post(
        "/tasks/",
        json={"title": title, "description": description},
    )


def test_create_task(client):
    response = create_task(
        client,
        title="Learn DevSecOps",
        description="Build a secure API",
    )

    assert response.status_code == 201
    assert response.json()["title"] == "Learn DevSecOps"
    assert response.json()["description"] == "Build a secure API"
    assert response.json()["completed"] is False
    assert "id" in response.json()


def test_create_task_strips_title_whitespace(client):
    response = create_task(client, title="  My task  ")

    assert response.status_code == 201
    assert response.json()["title"] == "My task"


def test_blank_title_is_rejected(client):
    response = create_task(client, title="   ")

    assert response.status_code == 422


def test_title_over_200_characters_is_rejected(client):
    response = create_task(client, title="x" * 201)

    assert response.status_code == 422


def test_description_over_2000_characters_is_rejected(client):
    response = create_task(client, description="x" * 2001)

    assert response.status_code == 422


def test_list_tasks(client):
    create_task(client, title="Task to list")

    response = client.get("/tasks/")

    assert response.status_code == 200
    assert any(task["title"] == "Task to list" for task in response.json())


def test_list_tasks_pagination(client):
    for title in ("First", "Second", "Third"):
        assert create_task(client, title=title).status_code == 201

    response = client.get("/tasks/?skip=1&limit=1")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["title"] == "Second"


def test_negative_skip_is_rejected(client):
    response = client.get("/tasks/?skip=-1")

    assert response.status_code == 422


def test_limit_over_100_is_rejected(client):
    response = client.get("/tasks/?limit=101")

    assert response.status_code == 422


def test_get_missing_task_returns_404(client):
    response = client.get("/tasks/999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"


def test_update_task(client):
    created = create_task(client, title="Original task")
    task_id = created.json()["id"]

    response = client.put(
        f"/tasks/{task_id}",
        json={"title": "Updated task", "completed": True},
    )

    assert response.status_code == 200
    assert response.json()["title"] == "Updated task"
    assert response.json()["completed"] is True


def test_update_with_empty_object_is_rejected(client):
    created = create_task(client)
    task_id = created.json()["id"]

    response = client.put(f"/tasks/{task_id}", json={})

    assert response.status_code == 422
    assert response.json()["detail"] == "Provide at least one field to update"


def test_update_missing_task_returns_404(client):
    response = client.put("/tasks/999999", json={"title": "Updated"})

    assert response.status_code == 404


def test_delete_task(client):
    created = create_task(client, title="Task to delete")
    task_id = created.json()["id"]

    response = client.delete(f"/tasks/{task_id}")

    assert response.status_code == 204
    assert client.get(f"/tasks/{task_id}").status_code == 404


def test_delete_missing_task_returns_404(client):
    response = client.delete("/tasks/999999")

    assert response.status_code == 404
