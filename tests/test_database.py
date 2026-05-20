from unittest.mock import Mock

from tasks_router.database.config_db import Settings
from tasks_router.database.initiate_db import Database


def test_settings_local_database_url_and_conn_args() -> None:
    settings = Settings(local=True)

    assert settings.get_db_url() == "sqlite:///./local.db"
    assert settings.get_conn_args() == {}


def test_settings_remote_database_url_and_conn_args() -> None:
    settings = Settings(
        local=False,
        host="db.example.com",
        port=5432,
        username="app_user",
        password="secret",
        database="tasks",
        sslmode="verify-full",
        sslrootcert="/cert.pem",
    )

    assert (
        settings.get_db_url()
        == "postgresql+psycopg2://app_user:secret@db.example.com:5432/tasks"
    )
    assert settings.get_conn_args() == {
        "sslmode": "verify-full",
        "sslrootcert": "/cert.pem",
    }


def test_database_get_engine_is_cached(monkeypatch) -> None:
    fake_engine = Mock()
    create_engine = Mock(return_value=fake_engine)
    monkeypatch.setattr(
        "tasks_router.database.initiate_db.create_engine",
        create_engine,
    )

    database = Database(Settings(local=True))

    first = database.get_engine()
    second = database.get_engine()

    assert first is second
    create_engine.assert_called_once()


def test_database_get_db_closes_session() -> None:
    database = Database(Settings(local=True))
    session = Mock()
    factory = Mock(return_value=session)
    database._session_factory = factory

    db_generator = database.get_db()
    yielded = next(db_generator)

    assert yielded is session

    try:
        next(db_generator)
    except StopIteration:
        pass

    session.close.assert_called_once()
