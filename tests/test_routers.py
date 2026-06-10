import uuid
import pytest
from tasks_router.main import app
from tasks_router.auth_placeholder import get_current_user_id


@pytest.mark.integration
def test_system_routes(client):
    health = client.get("/health")
    assert health.status_code == 200
    assert health.json() == {"service": "tasks-api", "status": "healthy"}

    root = client.get("/")
    assert root.status_code == 200
    assert "endpoints" in root.json()


@pytest.mark.integration
def test_user_routes(client, user_payload):
    # Create
    created = client.post("/users/", json=user_payload)
    assert created.status_code == 201
    created_data = created.json()
    assert created_data["username"] == user_payload["username"]
    assert created_data["display_name"] == user_payload["display_name"]

    # Get
    fetched = client.get(f"/users/{user_payload['username']}")
    assert fetched.status_code == 200
    fetched_data = fetched.json()
    assert fetched_data["username"] == user_payload["username"]
    assert fetched_data["display_name"] == user_payload["display_name"]


@pytest.mark.integration
def test_task_routes_crud(client, user_payload):
    # Setup user and auth
    client.post("/users/", json=user_payload)
    user_id = uuid.UUID(user_payload["id"])
    app.dependency_overrides[get_current_user_id] = lambda: user_id

    # List empty
    empty = client.get("/tasks/")
    assert empty.status_code == 200
    assert empty.json() == []

    # Create
    create_payload = {
        "title": "Write tests",
        "status": "todo",
        "dueDate": "2030-01-01T00:00:00Z",
    }
    created = client.post("/tasks/", json=create_payload)
    assert created.status_code == 201
    task_id = created.json()["id"]
    assert created.json()["title"] == "Write tests"
    assert created.json()["status"] == "todo"

    # List
    listed = client.get("/tasks/")
    assert listed.status_code == 200
    assert len(listed.json()) == 1
    assert listed.json()[0]["id"] == task_id

    # Update
    updated = client.patch(
        f"/tasks/{task_id}",
        json={"status": "done", "title": "Updated Title"},
    )
    assert updated.status_code == 200
    assert updated.json()["status"] == "done"
    assert updated.json()["title"] == "Updated Title"

    # Delete
    deleted = client.delete(f"/tasks/{task_id}")
    assert deleted.status_code == 204
    
    # Verify deletion
    assert client.get("/tasks/").json() == []
