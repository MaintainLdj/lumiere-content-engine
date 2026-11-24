from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://postgres:password@localhost:5432/aicontent"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
