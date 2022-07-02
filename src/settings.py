import os
from functools import lru_cache

from pydantic import BaseSettings


class Settings(BaseSettings):
    HOST: str
    PORT: int
    WEBSOCKETS_SUBPROTOCOL = "ocpp2.0.1"
    DEBUG: bool

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'
        case_sensitive = True


@lru_cache()
def get_settings():
    return Settings()


settings = get_settings()
