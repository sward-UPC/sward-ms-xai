from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
    database_url: str = "postgresql+asyncpg://sward:sward@localhost:5432/xai_db"
    redis_url: str = "redis://localhost:6379/0"
    explanation_cache_ttl: int = 3600
    aws_region: str = "us-east-1"
    eventbridge_bus_name: str = "sward-event-bus"
    environment: str = "development"
    service_name: str = "sward-ms-xai"
    # Orígenes permitidos para CORS (configurables por entorno).
    cors_allowed_origins: list[str] = ["http://localhost:5173"]

    @property
    def is_development(self) -> bool:
        return self.environment == "development"


settings = Settings()
