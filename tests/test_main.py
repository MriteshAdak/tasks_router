import uuid

import pytest

import tasks_router.auth_placeholder as auth_placeholder


@pytest.mark.e2e
def test_end_to_end_task_flow(client, user_payload):
	health = client.get("/health")
	assert health.status_code == 200

	created_user = client.post("/users", json=user_payload)
	assert created_user.status_code == 201
	auth_placeholder.MOCK_USER_ID = uuid.UUID(user_payload["id"])

	task_payload = {
		"title": "Ship release",
		"status": "in_progress",
		"due_date": "2031-06-01T12:00:00Z",
	}
	created_task = client.post("/tasks", json=task_payload)
	assert created_task.status_code == 201

	task_id = created_task.json()["id"]

	updated = client.patch(
		f"/tasks/{task_id}",
		json={"status": "done", "title": "Ship release v1"},
	)
	assert updated.status_code == 200
	assert updated.json()["status"] == "done"

	listed = client.get("/tasks")
	assert len(listed.json()) == 1

	deleted = client.delete(f"/tasks/{task_id}")
	assert deleted.status_code == 204
