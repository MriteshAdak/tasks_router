"""
Configuration module for database connection settings. This module defines a Settings class that uses Pydantic to manage database connection parameters, including host, port, username, password, database name, and SSL configuration. The Settings class provides methods to construct the database URL and connection arguments based on the provided settings. An instance of the Settings class is created at the end of the module for use in other parts of the application.
"""
import os
from typing import Optional
from urllib.parse import quote_plus

import structlog
from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

import boto3

ENV_FILE = ".env" if os.path.exists(".env") else None

class Settings(BaseSettings):

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        case_sensitive=False,
        extra="ignore",
    )

    # General configuration
    environment: str = "production"

    # Prebuilt URL
    url: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("DATABASE_URL", "DB_URL"),
    )

    # Stanalone connection parameters
    db_host: str = "localhost"
    db_port: int = 5432
    db_username: str = "postgres"
    db_password: str | None = None
    db_database: str = "psql"
    db_region: str = "eu-central-1"

    # SSL configuration
    db_sslmode: Optional[str] = None
    db_sslrootcert: Optional[str] = None

    # DB engine configuration
    echo: bool = False
    pool_pre_ping: bool = True
    pool_size: int = 10
    max_overflow: int = 20
    db_connect_retries: int = 3
    db_connect_retry_delay: float = 0.5

    # DB session configuration
    autocommit: bool = False
    autoflush: bool = False


    # TODO: Add logging here to log the loaded settings, ensuring that sensitive information like passwords is not logged. 
    # Adding validation for the settings to ensure they are correct before attempting to connect to the database.

    def generate_auth_token(self) -> str:
        """Generates an authentication token for AWS RDS using boto3."""
        structlog.get_logger(__name__).debug("db.settings.generating_auth_token")
        return boto3.client('rds', region_name=self.db_region) \
                  .generate_db_auth_token(
                    DBHostname=self.db_host,
                    Port=self.db_port, 
                    DBUsername=self.db_username, 
                    Region=self.db_region
            )

    def uses_iam_auth(self) -> bool:
        """Returns whether standalone DB settings should use RDS IAM auth."""
        return self.url is None and self.db_password is None
    
    def get_db_url(self) -> str:
        """Constructs the database URL from the settings."""

        if self.url is not None:
            structlog.get_logger(__name__).debug("db.settings.url_provided")
            return self.url

        if self.uses_iam_auth():
            structlog.get_logger(__name__).debug("db.settings.password_not_provided")
            password = "iam-auth-token"
        else:
            password = self.db_password
        
        safe_username = quote_plus(self.db_username)
        safe_password = quote_plus(password)
        
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
