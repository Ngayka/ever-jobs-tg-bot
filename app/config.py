from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    telegram_bot_token: str
    ever_jobs_api_url: str = "http://localhost:3001/graphql"
    database_url: str = "sqlite+aiosqlite:///./ever_jobs_bot.db"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
