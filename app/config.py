from pydantic_settings import BaseSettings
from functools import lru_cache
import logging
from typing import Dict

class Settings(BaseSettings):
    api_key: str
    azure_endpoint: str
    azure_api_key: str
    host: str = "0.0.0.0"
    port: int = 8000
    log_level: str = "INFO"

    model_config = {
        "env_file": ".env",
        "protected_namespaces": ()  # 完全禁用命名空间保护
    }

    def setup_logging(self):
        logging.basicConfig(
            level=self.log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

@lru_cache()
def get_settings():
    return Settings()
