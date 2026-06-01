"""
Configuration module for database connection settings. This module defines a Settings class that uses Pydantic to manage database connection parameters, including host, port, username, password, database name, and SSL configuration. The Settings class provides methods to construct the database URL and connection arguments based on the provided settings. An instance of the Settings class is created at the end of the module for use in other parts of the application.
"""

from typing import Optional
from urllib.parse import quote_plus

import structlog
from pydantic import AliasChoices, Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",
    )

    # General configuration
    environment: str = "development"

    # Prebuilt URL
    url: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("DATABASE_URL", "DB_URL"),
    )

    # Stanalone connection parameters
    db_host: str = "localhost"
    db_port: int = 5432
    db_username: str
    db_password: SecretStr
    db_database: str = "psql"

    # SSL configuration
    db_sslmode: Optional[str] = None
    db_sslrootcert: Optional[str] = None

    # DB engine configuration
    echo: bool = False
    pool_pre_ping: bool = True
    pool_size: int = 10
    max_overflow: int = 20

    # DB session configuration
    autocommit: bool = False
    autoflush: bool = False


    # TODO: Add logging here to log the loaded settings, ensuring that sensitive information like passwords is not logged. 
    # Adding validation for the settings to ensure they are correct before attempting to connect to the database.
    
    def get_db_url(self) -> str:
        """Constructs the database URL from the settings."""

        if self.url is not None:
            structlog.get_logger(__name__).debug("db.settings.url_provided")
            return self.url

        safe_username = quote_plus(self.db_username)
        safe_password = quote_plus(self.db_password.get_secret_value())

        structlog.get_logger(__name__).debug(
            "db.settings.url_constructed",
            host=self.db_host,
            port=self.db_port,
            database=self.db_database,
            sslmode=self.db_sslmode,
        )

        return f"postgresql+psycopg2://{safe_username}:{safe_password}@{self.db_host}:{self.db_port}/{self.db_database}"

    def get_conn_args(self) -> dict[str, str]:
        """Constructs the connection arguments from the settings."""

        if self.db_sslmode is None:
            structlog.get_logger(__name__).debug("db.settings.ssl.disabled")
            return {}
        elif self.db_sslmode in ("verify-ca", "verify-full"):
            structlog.get_logger(__name__).debug("db.settings.ssl.verify", sslmode=self.db_sslmode)
            return {
                "sslmode": self.db_sslmode,
                "sslrootcert": self.db_sslrootcert
            }
        else:
            structlog.get_logger(__name__).debug("db.settings.ssl.enabled", sslmode=self.db_sslmode)
            return {
                "sslmode": self.db_sslmode
            }

settings: Settings = Settings()