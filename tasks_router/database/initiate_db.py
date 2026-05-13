"""
This module defines the Database class, which manages the SQLAlchemy engine and session factory for the application. It provides methods to create and cache the engine and session factory, as well as a generator function to yield database sessions for use in request handling.
"""

from typing import Generator

from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import Session, sessionmaker, DeclarativeBase

from .config_db import Settings

class Base(DeclarativeBase):
    pass


class Database:

    def __init__(self, settings: Settings) -> None:
        """Initializes the Database instance with the provided settings."""

        self.db_url = settings.get_db_url()
        self.conn_args = settings.get_conn_args()
        self._engine: Engine | None = None
        self._session_factory: sessionmaker[Session] | None = None

    def get_engine(self) -> Engine:
        """Returns a cached Engine instance. Creates one if it doesn't exist."""

        if self._engine is None: # Move all these configuration params to a config file.
            self._engine = create_engine(
                self.db_url,
                echo=True,
                pool_pre_ping=True,
                connect_args=self.conn_args,
                pool_size=10,
                max_overflow=20
            )
        return self._engine

    def get_session_factory(self) -> sessionmaker[Session]:
        """Returns a cached sessionmaker bound to the engine."""
        
        if self._session_factory is None: # Move all these configuration params to a config file.
            self._session_factory = sessionmaker(
                self.get_engine(),
                autocommit=False,
                autoflush=False
            )
        return self._session_factory

    # Todo: decide if commit and rollback should be handled here or in the service layer.
    def get_db(self) -> Generator[Session, None, None]: 
        """Generates a new database session for each request. The session is closed after use."""
        
        db: Session = self.get_session_factory()()
        try:
            yield db
        finally:
            db.close()