"""
Application settings.

Everything that differs between environments (dev / staging / prod, or
SQLite vs PostgreSQL) lives here and is read from environment variables
(or a local .env file). Nothing else in the app should read os.environ
directly.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    environment: str = "development"

    # Default is SQLite so the project runs with zero external setup.
    # Swap to a PostgreSQL URL later without touching any other file:
    #   postgresql+psycopg2://user:password@host:5432/dbname
    database_url: str = "sqlite:///./pib_assessment.db"

    # Comma-separated list of allowed frontend origins for CORS.
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    allowed_hosts: str = "localhost,127.0.0.1"

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def allowed_hosts_list(self) -> list[str]:
        return [host.strip() for host in self.allowed_hosts.split(",") if host.strip()]


settings = Settings()
