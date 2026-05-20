from unittest.mock import Mock

from tasks_router import dependencies
from tasks_router.database.initiate_db import Database
from tasks_router.repositories.task_repo import TaskRepository
from tasks_router.repositories.user_repo import UserRepository
from tasks_router.services.task_service import TaskServices
from tasks_router.services.user_service import UserService


def test_get_db_yields_from_global_database(monkeypatch) -> None:
    session = Mock()
    mocked_db = Mock(spec=Database)
    mocked_db.get_db.return_value = iter([session])
    monkeypatch.setattr(dependencies, "db", mocked_db)

    db_gen = dependencies.get_db()

    yielded = next(db_gen)
    assert yielded is session

    try:
        next(db_gen)
    except StopIteration:
        pass

    mocked_db.get_db.assert_called_once()


def test_get_task_repository_returns_task_repository() -> None:
    session = Mock()

    repository = dependencies.get_task_repository(session)

    assert isinstance(repository, TaskRepository)
    assert repository.db_session is session


def test_get_user_repository_returns_user_repository() -> None:
    session = Mock()

    repository = dependencies.get_user_repository(session)

    assert isinstance(repository, UserRepository)
    assert repository.db_session is session


def test_get_task_services_returns_task_services() -> None:
    repo = Mock(spec=TaskRepository)

    service = dependencies.get_task_services(repo)

    assert isinstance(service, TaskServices)
    assert service.repository is repo


def test_get_user_services_returns_user_service() -> None:
    repo = Mock(spec=UserRepository)

    service = dependencies.get_user_services(repo)

    assert isinstance(service, UserService)
    assert service.repository is repo
