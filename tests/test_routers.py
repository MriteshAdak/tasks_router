import uuid

import pytest

import tasks_router.auth_placeholder as auth_placeholder


@pytest.mark.integration
def test_system_routes(client):
	health = client.get("/health")
	assert health.status_code == 200
	assert health.json()["status"] == "healthy"

	root = client.get("/")
	assert root.status_code == 200
	assert "endpoints" in root.json()


@pytest.mark.integration
def test_user_routes(client, user_payload):
	created = client.post("/users", json=user_payload)

	assert created.status_code == 201
	assert created.json()["username"] == user_payload["username"]

	fetched = client.get(f"/users/{user_payload['username']}")

	assert fetched.status_code == 200
	assert fetched.json()["display_name"] == user_payload["display_name"]


@pytest.mark.integration
def test_task_routes_crud(client, user_payload):
	client.post("/users", json=user_payload)
	auth_placeholder.MOCK_USER_ID = uuid.UUID(user_payload["id"])

	empty = client.get("/tasks")

	assert empty.status_code == 200
	assert empty.json() == []

	create_payload = {
		"title": "Write tests",
		"status": "todo",
		"dueDate": "2030-01-01T00:00:00Z",
	}
	created = client.post("/tasks", json=create_payload)

	assert created.status_code == 201
	task_id = created.json()["id"]
	assert created.json()["title"] == "Write tests"

	listed = client.get("/tasks")

	assert listed.status_code == 200
	assert len(listed.json()) == 1

	updated = client.patch(
		f"/tasks/{task_id}",
		json={"status": "done"},
	)

	assert updated.status_code == 200
	assert updated.json()["status"] == "done"

	deleted = client.delete(f"/tasks/{task_id}")

	assert deleted.status_code == 204
	assert client.get("/tasks").json() == []
