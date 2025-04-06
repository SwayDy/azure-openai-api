from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
import logging
import os

class Settings(BaseSettings):
    api_key: str
    azure_endpoint: str
    azure_api_key: str
    host: str = "0.0.0.0"
    port: int = 8000
    log_level: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        protected_namespaces=(),
        extra="ignore"
    )

    def setup_logging(self):
        """初始化结构化日志配置"""
        logging.config.fileConfig(
            'logging.conf',
            defaults={'log_level': self.log_level},
            disable_existing_loggers=False
        )

@lru_cache()
def get_settings():
    return Settings()
