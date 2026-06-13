import uuid
import pytest
from tasks_router.main import app
from tasks_router.auth_placeholder import get_current_user_id

@pytest.mark.integration
def test_get_user_not_found(client):
    response = client.get("/users/nonexistent_user")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

@pytest.mark.integration
def test_get_task_not_found(client, user_payload):
    # Create user and mock auth
    client.post("/users/", json=user_payload)
    user_id = uuid.UUID(user_payload["id"])
    app.dependency_overrides[get_current_user_id] = lambda: user_id
    
    # Using PATCH instead of GET because GET /{task_id} is not implemented
    response = client.patch(f"/tasks/{uuid.uuid4()}", json={"title": "Doesn't matter"})
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

@pytest.mark.integration
def test_create_task_invalid_payload(client, user_payload):
    client.post("/users/", json=user_payload)
    user_id = uuid.UUID(user_payload["id"])
    app.dependency_overrides[get_current_user_id] = lambda: user_id
    
    # Missing title
    response = client.post("/tasks/", json={"status": "todo"})
    assert response.status_code == 422

@pytest.mark.integration
def test_cross_tenant_access_denied(client, user_payload, db_session):
    # 1. Create User A and User B
    user_a_payload = user_payload
    user_b_payload = {
        "id": str(uuid.uuid4()),
        "username": "bob",
        "display_name": "Bob",
    }
    client.post("/users/", json=user_a_payload)
    client.post("/users/", json=user_b_payload)
    
    user_a_id = uuid.UUID(user_a_payload["id"])
    user_b_id = uuid.UUID(user_b_payload["id"])
    
    # 2. Create a task for User A
    app.dependency_overrides[get_current_user_id] = lambda: user_a_id
    task_response = client.post("/tasks/", json={"title": "User A Task"})
    assert task_response.status_code == 201
    task_id = task_response.json()["id"]
    
    # Try to access User A's task as User B
    app.dependency_overrides[get_current_user_id] = lambda: user_b_id
    
    # Update (should fail with 404 because User B doesn't own User A's task)
    response = client.patch(f"/tasks/{task_id}", json={"title": "Hacked"})
    assert response.status_code == 404
    
    # Delete
    response = client.delete(f"/tasks/{task_id}")
    assert response.status_code == 404
