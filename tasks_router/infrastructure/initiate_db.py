"""
This module defines the Database class, which manages the SQLAlchemy engine and session factory for the application. It provides methods to create and cache the engine and session factory, as well as a generator function to yield database sessions for use in request handling.
"""

import time
from typing import Any

import structlog
from sqlalchemy import Engine, create_engine, event, text
from sqlalchemy.pool import NullPool
from sqlalchemy.orm import Session, sessionmaker

from .configurations import Settings


class Database:

    def __init__(self, settings: Settings) -> None:
        """Initializes the Database instance with the provided settings."""

        self.settings = settings
        self._logger = structlog.get_logger(__name__)
        self._engine: Engine = self._create_engine()
        self._session_factory: sessionmaker[Session] = self._create_session_factory()
        self._probe_connection()

    def _register_connection_handler(self, engine: Engine) -> None:
        """Refresh IAM tokens for new connections."""

        @event.listens_for(engine, "do_connect")
        def connect_with_iam_token( # type: ignore
            dialect: Any,
            conn_rec: Any,
            cargs: tuple[Any, ...],
            cparams: dict[str, Any],
        ) -> Any:
            if self.settings.uses_iam_auth():
                cparams["password"] = self.settings.generate_auth_token()

            return dialect.connect(*cargs, **cparams)

    def _create_engine(self) -> Engine:
        self._logger.info(
            "db.engine.create",
            host=self.settings.db_host,
            port=self.settings.db_port,
            database=self.settings.db_database,
            sslmode=self.settings.db_sslmode,
        )

        engine = create_engine(
            self.settings.get_db_url(),
            poolclass=NullPool,
            echo=self.settings.echo,
            connect_args={
                **self.settings.get_conn_args(),
                "connect_timeout": self.settings.connect_timeout_seconds,
                "options": "-c statement_timeout=30000",
            },
        )
        self._register_connection_handler(engine)
        return engine

    def _create_session_factory(self) -> sessionmaker[Session]:
        self._logger.info("db.session_factory.create")
        return sessionmaker(
            self._engine,
            autocommit=self.settings.autocommit,
            autoflush=self.settings.autoflush,
        )

    def ping_database(self) -> bool:
        """Explicitly pings the database to verify reachability."""
        try:
            with self._engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return True
        except Exception as e:
            self._logger.error("db.ping.failed", error=str(e))
            return False

    def _probe_connection(self) -> None:
        """Validates Aurora is reachable at cold start."""
        last_exception: Exception | None = None
        retries = self.settings.probe_max_retries
        wait = self.settings.probe_retry_wait_seconds
        
        for attempt in range(retries):
            try:
                with self._engine.connect() as conn:
                    conn.execute(text("SELECT 1"))
                self._logger.info("db.probe.success", attempt=attempt + 1)
                return
            except Exception as exc:
                last_exception = exc
                self._logger.warning(
                    "db.probe.retry",
                    attempt=attempt + 1,
                    retries=retries,
                    retry_delay=wait,
                    error=str(exc),
                )
                if attempt + 1 < retries:
                    time.sleep(wait)

        self._logger.exception("db.probe.failed", error=str(last_exception))
        raise RuntimeError(
            "Could not establish a database connection after %d attempts at cold start." % retries
        )

    def get_engine(self) -> Engine:
        """Returns the initialized Engine instance."""
        return self._engine

    def get_session_factory(self) -> sessionmaker[Session]:
        """Returns the initialized session factory."""
        return self._session_factory

    def get_db(self) -> Session:
        """Creates a new SQLAlchemy Session for the current request."""
        return self._session_factory()
