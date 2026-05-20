"""
Configuration for database connection settings.

Settings is loaded from environment variables and used to build
database URL and connection arguments.
"""

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

    # Validation is deferred so runtime profile loading stays simple.
    def get_db_url(self) -> str:
        """Build the database URL for SQLAlchemy.

        Returns:
            SQLAlchemy connection URL for local or remote DB use.
        """

        if self.local:
            return "sqlite:///./local.db"
        
        return f"postgresql+psycopg2://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"
    
    def get_conn_args(self) -> dict[str, str]:
        """Build optional connection arguments.

        Returns:
            DB driver connection arguments for SSL-enabled environments.
        """

        if self.local:
            return {}
        
        return {
            "sslmode": self.sslmode,
            "sslrootcert": self.sslrootcert
        }    

settings: Settings = Settings()
