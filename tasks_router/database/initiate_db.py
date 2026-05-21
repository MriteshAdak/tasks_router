"""
Database engine and session factory management.

The Database class centralizes engine and session creation so request
handlers can reuse a consistent connection strategy.
"""

from typing import Generator

from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import Session, sessionmaker, DeclarativeBase

from .config_db import Settings

class Base(DeclarativeBase):
    pass


class Database:

    def __init__(self, settings: Settings) -> None:
        """Initialize the database manager.

        Args:
            settings: Resolved database settings.
        """

        self.db_url = settings.get_db_url()
        self.conn_args = settings.get_conn_args()
        self._engine: Engine | None = None
        self._session_factory: sessionmaker[Session] | None = None

    def get_engine(self) -> Engine:
        """Return a cached SQLAlchemy engine.

        Returns:
            Initialized SQLAlchemy engine instance.
        """

        # TODO: Implement exception handling and logging for database
        # connection issues. Consider retry logic for transient errors.
        if self._engine is None:  # Move configuration params to config.
            self._engine = create_engine(
                self.db_url,
                echo=True,
                pool_pre_ping=True,
                connect_args=self.conn_args,
                pool_size=10,
                max_overflow=20
            )
        return self._engine

    # TODO: Implement exception handling and logging for session
    # creation issues.
    def get_session_factory(self) -> sessionmaker[Session]:
        """Return a cached session factory.

        Returns:
            Session factory bound to the shared engine.
        """

        if self._session_factory is None:  # Move configuration params.
            self._session_factory = sessionmaker(
                self.get_engine(),
                autocommit=False,
                autoflush=False
            )
        return self._session_factory

    # TODO: decide if commit and rollback should be handled here or in
    # the service layer.
    def get_db(self) -> Generator[Session, None, None]:
        """Yield a database session and close it after use.

        Yields:
            Request-scoped SQLAlchemy session.
        """

        db: Session = self.get_session_factory()()
        try:
            yield db
        finally:
            db.close()
