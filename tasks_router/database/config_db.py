"""
Configuration module for database connection settings. This module defines a Settings class that uses Pydantic to manage database connection parameters, including host, port, username, password, database name, and SSL configuration. The Settings class provides methods to construct the database URL and connection arguments based on the provided settings. An instance of the Settings class is created at the end of the module for use in other parts of the application.
"""

from urllib.parse import quote_plus

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr

class Settings(BaseSettings):

    url: str = None
    host: str = "localhost"
    port: int = 5432
    username: str = "user"
    password: SecretStr = SecretStr("password")
    database: str = "psql"
    sslmode: str = None
    sslrootcert: str = None

    model_config = SettingsConfigDict(env_file=".env", env_prefix="DB_")

    # TODO: Add logging here to log the loaded settings, ensuring that sensitive information like passwords is not logged. 
    # Adding validation for the settings to ensure they are correct before attempting to connect to the database.
    
    def get_db_url(self) -> str:
        """Constructs the database URL from the settings."""

        safe_username = quote_plus(self.username)
        safe_password = quote_plus(self.password.get_secret_value())
        if self.url is not None:
            return self.url
        
        return f"postgresql+psycopg2://{safe_username}:{safe_password}@{self.host}:{self.port}/{self.database}"

    def get_conn_args(self) -> dict[str, str]:
        """Constructs the connection arguments from the settings."""

        if self.sslmode is None:
            return {}
        elif self.sslmode in ("verify-ca", "verify-full"):
            return {
                "sslmode": self.sslmode,
                "sslrootcert": self.sslrootcert
            }
        else:
            return {
                "sslmode": self.sslmode
            }

settings: Settings = Settings()