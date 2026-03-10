from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    app_name: str = "智能排班系统"
    database_url: str = "sqlite:///./scheduler.db"
    debug: bool = True

    class Config:
        env_file = ".env"


settings = Settings()
