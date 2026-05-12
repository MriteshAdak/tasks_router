from .config_db import Settings
from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import Session, sessionmaker, DeclarativeBase
from typing import Generator


class Base(DeclarativeBase):
    pass


class Database:

    def __init__(self, settings: Settings) -> None:
        self.db_url = settings.get_db_url()
        self._engine: Engine | None = None
        self._session_factory: sessionmaker[Session] | None = None

    def get_engine(self) -> Engine:
        """Returns a cached Engine instance. Creates one if it doesn't exist."""

        if self._engine is None:
            self._engine = create_engine(
                self.db_url,
                echo=True,           
                pool_pre_ping=True,  
                pool_size=10,        
                max_overflow=20,
            )
        return self._engine

    def get_session_factory(self) -> sessionmaker[Session]:
        """Returns a cached sessionmaker bound to the engine."""
        
        if self._session_factory is None:
            self._session_factory = sessionmaker(
                self.get_engine(),
                autocommit=False,
                autoflush=False
            )
        return self._session_factory

    def create_tables(self) -> None:
        """Creates all tables defined on Base."""

        Base.metadata.create_all(bind=self.get_engine())

    def get_db(self) -> Generator[Session, None, None]:
        """
        Generates a new database session for each request. Commits the transaction if successful, rolls back if an exception occurs, and ensures the session is closed after use.
        """
        session_factory: sessionmaker[Session] = self.get_session_factory()
        db: Session = session_factory()
        try:
            yield db
        finally:
            db.close()