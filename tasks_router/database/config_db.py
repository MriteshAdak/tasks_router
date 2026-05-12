from pydantic_settings import BaseSettings, SettingsConfigDict

# placeholder for database configuration settings. Dummy values are provided for now.

class Settings(BaseSettings):

    host: str = "localhost"
    port: int = 5432
    username: str = "user"
    password: str = "password"
    database: str = "tasks_db"
    ssl_mode: str = "verify-full"

    model_config = SettingsConfigDict(env_file=".env")

    def get_db_url(self) -> str:
        return f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"
    
settings: Settings = Settings()