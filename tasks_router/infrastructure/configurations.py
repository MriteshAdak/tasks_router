"""
Configuration module for database connection settings. This module defines a Settings class that uses Pydantic to manage database connection parameters, including host, port, username, password, database name, and SSL configuration. The Settings class provides methods to construct the database URL and connection arguments based on the provided settings. An instance of the Settings class is created at the end of the module for use in other parts of the application.
"""

from typing import Optional
from urllib.parse import quote_plus

import structlog
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr

class Settings(BaseSettings):

    model_config = SettingsConfigDict(env_file=".env", env_prefix="DB_")

    # General configuration
    environment: str = "development"

    # Prebuilt URL
    url: Optional[str] = None

    # Stanalone connection parameters
    host: str = "localhost"
    port: int = 5432
    username: str
    password: SecretStr
    database: str = "psql"

    # SSL configuration
    sslmode: Optional[str] = None
    sslrootcert: Optional[str] = None

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

        safe_username = quote_plus(self.username)
        safe_password = quote_plus(self.password.get_secret_value())

        structlog.get_logger(__name__).debug(
            "db.settings.url_constructed",
            host=self.host,
            port=self.port,
            database=self.database,
            sslmode=self.sslmode,
        )

        return f"postgresql+psycopg2://{safe_username}:{safe_password}@{self.host}:{self.port}/{self.database}"

    def get_conn_args(self) -> dict[str, str]:
        """Constructs the connection arguments from the settings."""

        if self.sslmode is None:
            structlog.get_logger(__name__).debug("db.settings.ssl.disabled")
            return {}
        elif self.sslmode in ("verify-ca", "verify-full"):
            structlog.get_logger(__name__).debug("db.settings.ssl.verify", sslmode=self.sslmode)
            return {
                "sslmode": self.sslmode,
                "sslrootcert": self.sslrootcert
            }
        else:
            structlog.get_logger(__name__).debug("db.settings.ssl.enabled", sslmode=self.sslmode)
            return {
                "sslmode": self.sslmode
            }

settings: Settings = Settings()