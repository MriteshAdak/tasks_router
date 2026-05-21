"""
Configuration module for database connection settings. This module defines a Settings class that uses Pydantic to manage database connection parameters, including host, port, username, password, database name, and SSL configuration. The Settings class provides methods to construct the database URL and connection arguments based on the provided settings. An instance of the Settings class is created at the end of the module for use in other parts of the application.
"""

from urllib.parse import quote

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    local: bool = False

    host: str = "localhost"
    port: int = 5432
    username: str = "user"
    password: str = "password"
    database: str = "tasks_db"
    sslmode: str = "verify-full"
    sslrootcert: str = "./global-bundle.pem"

    model_config = SettingsConfigDict(env_file=".env")

    # TODO: Add logging here to log the loaded settings, ensuring that sensitive information like passwords is not logged. 
    # Adding validation for the settings to ensure they are correct before attempting to connect to the database.
    
    def get_db_url(self) -> str:
        """Constructs the database URL from the settings."""

        if self.local:
            return "sqlite:///./local.db"

        encoded_username = quote(self.username, safe="")
        encoded_password = quote(self.password, safe="")
        return f"postgresql+psycopg2://{encoded_username}:{encoded_password}@{self.host}:{self.port}/{self.database}"
    
    def get_conn_args(self) -> dict[str, str]:
        """Constructs the connection arguments from the settings."""

        if self.local:
            return {}
        
        return {
            "sslmode": self.sslmode,
            "sslrootcert": self.sslrootcert
        }    

settings: Settings = Settings()
