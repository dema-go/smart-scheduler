from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Optional


class Settings(BaseSettings):
    """应用配置"""
    app_name: str = "智能排班系统"
    app_title: str = "智能排班系统 API"
    database_url: str = "sqlite:///./scheduler.db"
    debug: bool = True

    # CORS 配置
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    cors_allow_credentials: bool = True
    cors_allow_methods: str = "*"
    cors_allow_headers: str = "*"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @property
    def cors_origins_list(self) -> List[str]:
        """将 CORS origins 字符串转换为列表"""
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


settings = Settings()
