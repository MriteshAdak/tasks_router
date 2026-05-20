from unittest.mock import Mock

from fastapi.testclient import TestClient

from tasks_router import main


def test_app_includes_expected_routes() -> None:
    paths = {route.path for route in main.app.routes}

    assert "/" in paths
    assert "/health" in paths
    assert "/tasks/" in paths
    assert "/users/{username}" in paths


def test_lifespan_creates_tables_and_disposes_engine(monkeypatch) -> None:
    engine = Mock()
    create_all = Mock()
    monkeypatch.setattr(main.db, "get_engine", lambda: engine)
    monkeypatch.setattr(main.Base.metadata, "create_all", create_all)

    with TestClient(main.app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    create_all.assert_called_once_with(engine)
    engine.dispose.assert_called_once()
