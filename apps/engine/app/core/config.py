from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables.

    Database defaults to Supabase CLI's local Postgres (port 54322).
    In production, set DATABASE_URL to the remote Supabase connection string.
    """

    app_name: str = "Gridlane Engine"
    debug: bool = False
    api_version: str = "v1"

    # Database — Supabase Postgres (local CLI default: port 54322)
    database_url: str = (
        "postgresql+asyncpg://postgres:postgres@localhost:54322/postgres"
    )

    # Redis (queue broker — used by pipeline execution in future)
    redis_url: str = "redis://localhost:6379/0"

    # CORS
    allowed_origins: list[str] = ["http://localhost:3000"]

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
