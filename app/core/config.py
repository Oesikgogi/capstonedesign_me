from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "BOO Backend"
    database_url: str = "sqlite:///./app.db"
    secret_key: str = "change-this-secret-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 14

    timezone: str = "Asia/Seoul"

    breakfast_start_hour: int = 8
    breakfast_end_hour: int = 10
    lunch_start_hour: int = 11
    lunch_end_hour: int = 14
    dinner_start_hour: int = 17
    dinner_end_hour: int = 19

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
