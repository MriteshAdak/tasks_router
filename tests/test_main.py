import uuid
import pytest
from tasks_router.main import app
from tasks_router.auth_placeholder import get_current_user_id


@pytest.mark.e2e
def test_end_to_end_task_flow(client, user_payload):
    # 1. Check Health
    health = client.get("/health")
    assert health.status_code == 200
    assert health.json() == {"service": "tasks-api", "status": "healthy"}

    # 2. Create User
    created_user = client.post("/users/", json=user_payload)
    assert created_user.status_code == 201
    assert created_user.json()["username"] == user_payload["username"]
    
    # 3. Mock Authentication for subsequent requests
    user_id = uuid.UUID(user_payload["id"])
    app.dependency_overrides[get_current_user_id] = lambda: user_id

    # 4. Create Task
    task_payload = {
        "title": "Ship release",
        "status": "in_progress",
        "dueDate": "2031-06-01T12:00:00Z",
    }
    created_task = client.post("/tasks/", json=task_payload)
    assert created_task.status_code == 201
    task_data = created_task.json()
    assert task_data["title"] == task_payload["title"]
    assert task_data["status"] == task_payload["status"]
    assert task_data["id"] is not None

    task_id = task_data["id"]

    # 5. Update Task
    updated = client.patch(
        f"/tasks/{task_id}",
        json={"status": "done", "title": "Ship release v1"},
    )
    assert updated.status_code == 200
    updated_data = updated.json()
    assert updated_data["status"] == "done"
    assert updated_data["title"] == "Ship release v1"

    # 6. List Tasks
    listed = client.get("/tasks/")
    assert listed.status_code == 200
    listed_data = listed.json()
    assert len(listed_data) == 1
    assert listed_data[0]["id"] == task_id
    assert listed_data[0]["title"] == "Ship release v1"

    # 7. Delete Task
    deleted = client.delete(f"/tasks/{task_id}")
    assert deleted.status_code == 204

    # 8. Verify Deletion
    after_delete = client.get("/tasks/")
    assert len(after_delete.json()) == 0
