from unittest.mock import Mock

import pytest
from pydantic import ValidationError

from tasks_router.database.config_db import Settings
from tasks_router.database.initiate_db import Database


def _clear_settings_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for env_name in (
        "LOCAL",
        "HOST",
        "PORT",
        "USERNAME",
        "PASSWORD",
        "DATABASE",
        "SSLMODE",
        "SSLROOTCERT",
    ):
        monkeypatch.delenv(env_name, raising=False)


def test_settings_get_db_url_local_true_returns_sqlite() -> None:
    settings = Settings(local=True)

    assert settings.get_db_url() == "sqlite:///./local.db"


def test_settings_get_db_url_default_postgresql_values() -> None:
    settings = Settings(local=False)

    assert (
        settings.get_db_url()
        == "postgresql+psycopg2://user:password@localhost:5432/tasks_db"
    )


def test_settings_get_db_url_custom_postgresql_values() -> None:
    settings = Settings(
        local=False,
        host="db.example.com",
        port=6543,
        username="app_user",
        password="secret",
        database="tasks",
    )

    assert (
        settings.get_db_url()
        == "postgresql+psycopg2://app_user:secret@db.example.com:6543/tasks"
    )


def test_settings_get_db_url_preserves_special_characters() -> None:
    settings = Settings(
        local=False,
        username="user+name@corp",
        password="p@ss:word/with?chars",
    )

    assert (
        settings.get_db_url()
        == "postgresql+psycopg2://user%2Bname%40corp:p%40ss%3Aword%2Fwith%3Fchars@localhost:5432/tasks_db"
    )


def test_settings_get_db_url_allows_empty_credentials() -> None:
    settings = Settings(local=False, username="", password="")

    assert settings.get_db_url() == "postgresql+psycopg2://:@localhost:5432/tasks_db"


def test_settings_get_conn_args_local_true_returns_empty_dict() -> None:
    settings = Settings(local=True)

    assert settings.get_conn_args() == {}


def test_settings_get_conn_args_remote_defaults() -> None:
    settings = Settings(local=False)

    assert settings.get_conn_args() == {
        "sslmode": "verify-full",
        "sslrootcert": "./global-bundle.pem",
    }


def test_settings_get_conn_args_remote_custom_ssl_overrides() -> None:
    settings = Settings(local=False, sslmode="require", sslrootcert="/custom-ca.pem")

    assert settings.get_conn_args() == {
        "sslmode": "require",
        "sslrootcert": "/custom-ca.pem",
    }


def test_settings_loads_values_from_environment(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _clear_settings_env(monkeypatch)
    monkeypatch.setenv("LOCAL", "true")
    monkeypatch.setenv("PORT", "7001")
    monkeypatch.setenv("HOST", "env.db.local")
    monkeypatch.setenv("USERNAME", "env_user")

    settings = Settings()

    assert settings.local is True
    assert settings.port == 7001
    assert settings.host == "env.db.local"
    assert settings.username == "env_user"


def test_settings_invalid_port_in_environment_raises_validation_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _clear_settings_env(monkeypatch)
    monkeypatch.setenv("PORT", "not-an-int")

    with pytest.raises(ValidationError):
        Settings()


def test_settings_defaults_applied_when_env_unset(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _clear_settings_env(monkeypatch)

    settings = Settings()

    assert settings.local is False
    assert settings.host == "localhost"
    assert settings.port == 5432
    assert settings.username == "user"
    assert settings.password == "password"
    assert settings.database == "tasks_db"
    assert settings.sslmode == "verify-full"
    assert settings.sslrootcert == "./global-bundle.pem"


def test_database_get_engine_calls_create_engine_with_expected_arguments(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake_settings = Mock(spec=Settings)
    fake_settings.get_db_url.return_value = "postgresql+psycopg2://u:p@h:5432/db"
    fake_settings.get_conn_args.return_value = {
        "sslmode": "require",
        "sslrootcert": "/ca",
    }
    fake_engine = Mock()
    create_engine_mock = Mock(return_value=fake_engine)
    monkeypatch.setattr(
        "tasks_router.database.initiate_db.create_engine",
        create_engine_mock,
    )

    database = Database(fake_settings)

    engine = database.get_engine()

    assert engine is fake_engine
    create_engine_mock.assert_called_once_with(
        "postgresql+psycopg2://u:p@h:5432/db",
        echo=True,
        pool_pre_ping=True,
        connect_args={"sslmode": "require", "sslrootcert": "/ca"},
        pool_size=10,
        max_overflow=20,
    )


def test_database_get_engine_is_cached_and_create_engine_called_once(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake_settings = Mock(spec=Settings)
    fake_settings.get_db_url.return_value = "sqlite:///./local.db"
    fake_settings.get_conn_args.return_value = {}
    fake_engine = Mock()
    create_engine_mock = Mock(return_value=fake_engine)
    monkeypatch.setattr(
        "tasks_router.database.initiate_db.create_engine",
        create_engine_mock,
    )
    database = Database(fake_settings)

    first = database.get_engine()
    second = database.get_engine()

    assert first is second
    create_engine_mock.assert_called_once_with(
        "sqlite:///./local.db",
        echo=True,
        pool_pre_ping=True,
        connect_args={},
        pool_size=10,
        max_overflow=20,
    )


def test_database_get_engine_recreates_when_engine_cache_reset(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake_settings = Mock(spec=Settings)
    fake_settings.get_db_url.return_value = "sqlite:///./local.db"
    fake_settings.get_conn_args.return_value = {}
    first_engine = Mock()
    second_engine = Mock()
    create_engine_mock = Mock(side_effect=[first_engine, second_engine])
    monkeypatch.setattr(
        "tasks_router.database.initiate_db.create_engine",
        create_engine_mock,
    )
    database = Database(fake_settings)

    initial = database.get_engine()
    database._engine = None
    recreated = database.get_engine()

    assert initial is first_engine
    assert recreated is second_engine
    assert create_engine_mock.call_count == 2


def test_database_get_session_factory_uses_sessionmaker_and_caches(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    database = Database(Settings(local=True))
    fake_engine = Mock()
    fake_factory = Mock()
    get_engine_mock = Mock(return_value=fake_engine)
    sessionmaker_mock = Mock(return_value=fake_factory)
    monkeypatch.setattr(database, "get_engine", get_engine_mock)
    monkeypatch.setattr(
        "tasks_router.database.initiate_db.sessionmaker",
        sessionmaker_mock,
    )

    first = database.get_session_factory()
    second = database.get_session_factory()

    assert first is fake_factory
    assert second is first
    sessionmaker_mock.assert_called_once_with(
        fake_engine,
        autocommit=False,
        autoflush=False,
    )
    get_engine_mock.assert_called_once_with()


def test_database_get_db_yields_and_closes_after_exhaustion() -> None:
    database = Database(Settings(local=True))
    session = Mock()
    factory = Mock(return_value=session)
    database._session_factory = factory

    db_gen = database.get_db()
    yielded = next(db_gen)

    assert yielded is session
    with pytest.raises(StopIteration):
        next(db_gen)
    factory.assert_called_once_with()
    session.close.assert_called_once_with()


def test_database_get_db_closes_session_when_iteration_raises() -> None:
    database = Database(Settings(local=True))
    session = Mock()
    factory = Mock(return_value=session)
    database._session_factory = factory

    db_gen = database.get_db()
    _ = next(db_gen)

    with pytest.raises(RuntimeError, match="consumer failure"):
        db_gen.throw(RuntimeError("consumer failure"))
    factory.assert_called_once_with()
    session.close.assert_called_once_with()
