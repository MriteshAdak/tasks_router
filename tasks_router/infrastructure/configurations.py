"""
Configuration module for database connection settings. This module defines a Settings class that uses Pydantic to manage database connection parameters, including host, port, username, password, database name, and SSL configuration. The Settings class provides methods to construct the database URL and connection arguments based on the provided settings. An instance of the Settings class is created at the end of the module for use in other parts of the application.
"""
import os
from datetime import datetime, timedelta, timezone
from typing import Any, Optional
from urllib.parse import quote_plus

import structlog
from pydantic import AliasChoices, Field, PrivateAttr
from pydantic_settings import BaseSettings, SettingsConfigDict

import boto3 # type: ignore

ENV_FILE = ".env" if os.path.exists(".env") else None

class Settings(BaseSettings):

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        case_sensitive=False,
        extra="ignore",
    )

    # Cache for RDS IAM Auth Token
    _cached_token: Optional[str] = PrivateAttr(default=None)
    _token_expiry: Optional[datetime] = PrivateAttr(default=None)

    # General configuration
    environment: str = "production"

    # Prebuilt URL
    url: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("DATABASE_URL", "DB_URL"),
    )

    # Standalone connection parameters
    db_host: Optional[str] = None
    db_port: Optional[int] = None
    db_username: Optional[str] = None
    db_password: Optional[str] = None
    db_database: Optional[str] = None
    db_region: str = "eu-central-1"

    # SSL configuration
    db_sslmode: Optional[str] = None
    db_sslrootcert: Optional[str] = None

    connect_timeout_seconds: int = 40
    probe_max_retries: int = 3
    probe_retry_wait_seconds: float = 2.0

    def __init__(self, **values: Any) -> None:
        super().__init__(**values)
        self._validate_db_settings()

    def _validate_db_settings(self) -> None:
        if self.url is not None:
            return

        required_fields: dict[str, Any]= {
            "db_host": self.db_host,
            "db_port": self.db_port,
            "db_username": self.db_username,
            "db_database": self.db_database,
        }

        missing = [name for name, value in required_fields.items() if not value]

        if self.uses_iam_auth():
            if missing:
                raise RuntimeError(
                    "RDS IAM auth requires db_host, db_port, db_username, and db_database to be set."
                )
        else:
            if self.db_password is None:
                missing.append("db_password")
            if missing:
                raise RuntimeError(
                    "Database configuration is incomplete. Set DATABASE_URL or provide "
                    "db_host, db_port, db_username, db_password, and db_database."
                )

        if self.db_sslmode in ("verify-ca", "verify-full") and not self.db_sslrootcert:
            raise RuntimeError(
                "db_sslrootcert is required when db_sslmode is verify-ca or verify-full."
            )

    # DB engine configuration
    echo: bool = False
    # DB session configuration
    autocommit: bool = False
    autoflush: bool = False

    def generate_auth_token(self) -> str:
        """Generates an authentication token for AWS RDS using boto3 with caching."""
        logger = structlog.get_logger(__name__)

        # Check if we have a valid cached token (valid for 15 mins, we cache for 10)
        now = datetime.now(timezone.utc)
        if self._cached_token and self._token_expiry and now < self._token_expiry:
            logger.debug("db.settings.using_cached_auth_token")
            return self._cached_token

        logger.info("db.settings.generating_new_auth_token")

        try:
            token = boto3.client( #type: ignore
                'rds', region_name=self.db_region
            ).generate_db_auth_token( #type: ignore
                DBHostname=self.db_host,
                Port=self.db_port,
                DBUsername=self.db_username,
                Region=self.db_region
            )
            self._cached_token = token # type: ignore
            # IAM tokens are valid for 15 minutes, we cache for 10 minutes to be safe
            self._token_expiry = now + timedelta(minutes=10)
            return token #type: ignore
        except Exception as e:
            logger.exception(
                "db.settings.auth_token_generation_failed",
                error=str(e),
                db_host=self.db_host,
                db_region=self.db_region,
            )
            raise

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
            self.db_password = self.generate_auth_token()
        
        safe_username = quote_plus(self.db_username) # type: ignore
        safe_password = quote_plus(self.db_password) # type: ignore
        
        structlog.get_logger(__name__).debug(
            "db.settings.url_constructed",
            host=self.db_host,
            port=self.db_port,
            database=self.db_database,
            sslmode=self.db_sslmode,
        )

        return f"postgresql+psycopg2://{safe_username}:{safe_password}@{self.db_host}:{self.db_port}/{self.db_database}"

    def get_conn_args(self) -> dict[str, str | None]:
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
