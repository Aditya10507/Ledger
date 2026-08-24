from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Central app configuration, loaded from environment variables / .env file."""

    database_url: str = "sqlite:///./ledger.db"

    jwt_secret: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expiry_hours: int = 24

    anthropic_api_key: str = ""

    max_upload_size_mb: int = 10
    cors_origins: list[str] = ["http://localhost:5173"]

    class Config:
        env_file = ".env"


settings = Settings()
