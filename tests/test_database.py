import pytest
from sqlalchemy.orm import Session

from tasks_router.infrastructure.configurations import Settings
from tasks_router.infrastructure.initiate_db import Database


@pytest.mark.unit
def test_database_engine_cached():
	settings = Settings(
		username="user",
		password="pass",
		url="sqlite+pysqlite:///:memory:",
	)
	db = Database(settings)

	engine_one = db.get_engine()
	engine_two = db.get_engine()

	assert engine_one is engine_two


@pytest.mark.unit
def test_database_session_factory_cached():
	settings = Settings(
		username="user",
		password="pass",
		url="sqlite+pysqlite:///:memory:",
	)
	db = Database(settings)

	factory_one = db.get_session_factory()
	factory_two = db.get_session_factory()

	assert factory_one is factory_two


@pytest.mark.unit
def test_database_get_db_yields_session():
	settings = Settings(
		username="user",
		password="pass",
		url="sqlite+pysqlite:///:memory:",
	)
	db = Database(settings)

	generator = db.get_db()
	session = next(generator)

	assert isinstance(session, Session)
	generator.close()
