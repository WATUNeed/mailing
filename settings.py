import logging
from datetime import datetime
import os

import pydantic
from pydantic import Field

from utils.time_utils import get_current_date


class Settings(pydantic.BaseSettings):
    # FastAPI settings.
    TITLE: str = Field(default='Mailing API')
    DESCRIPTION: str = Field(default='Automated mailing service.')
    VERSION: str = Field(default='1.0.1')
    DEBUG: bool = Field(default=True)

    # Describes the application settings.
    WEB_HOST: str = Field(default=os.getenv('WEB_HOST'))
    WEB_PORT: int = Field(default=os.getenv('WEB_PORT'))
    RELOAD: bool = Field(default=False)
    LOGGING_LEVEL: int = Field(default=logging.DEBUG)

    # Database settings.
    DB_DRIVER: str = Field(default=os.getenv('DB_DRIVER'))
    DB_HOST: str = Field(default=os.getenv('DB_HOST'))
    DB_PORT: str = Field(default=os.getenv('DB_PORT'))
    DB_NAME: str = Field(default=os.getenv('DB_NAME'))
    DB_USER: str = Field(default=os.getenv('DB_USER'))
    DB_PASS: str = Field(default=os.getenv('DB_PASS'))

    # Redis
    REDIS_DRIVER: str = Field(default='redis')
    REDIS_HOST: str = Field(default=os.getenv('REDIS_HOST'))
    REDIS_PORT: int = Field(default=os.getenv('REDIS_PORT'))
    REDIS_ENCODING: str = Field(default='utf8')
    DECODE_RESPONSES: bool = Field(default=True)

    # File logging.
    FILE_LOGGING_LEVEL: int = Field(logging.ERROR)
    FILE_MAX_BYTES: int = Field(default=10 * 1024 * 1024)  # 10MB
    FILE_BACKUP_COUNT: int = Field(default=5)
    FILE_LOGGING_FILENAME: str = Field("logs/error_log")
    LOGGING_FORMAT: str = Field("%(levelname)s: [%(asctime)s] - %(message)s")
    LOGGING_DATEFMT: str = Field("%Y-%m-%d %H:%M:%S")
    FILE_LOGGING_MODE: str = Field('a+')

    # Middleware
    ORIGINS: list[str] = Field(default=[
            'http://localhost',
            'http://localhost:8080',
            f'http://{WEB_HOST}:{WEB_PORT}',
        ]
    )
    ALLOW_METHODS: list[str] = Field(default=["*"])
    ALLOW_HEADERS: list[str] = Field(default=["*"])
    ALLOW_CREDENTIALS: bool = Field(default=True)

    # External mailing API settings.
    MAILING_API_URL: str = Field(default='https://probe.fbrq.cloud/v1/send/')
    MAILING_API_HEADERS: dict = Field(default={
        'accept': 'application/json',
        'Authorization': f'Bearer {os.getenv("AUTH_TOKEN")}',
        'Content-Type': 'application/json',
    })

    # Mailing queue
    MAILING_OFFSET_MIN: int = Field(default=5)
    TIMEOUT: int = Field(default=20)
    LATEST_QUEUE_DATE: datetime = Field(default=get_current_date())
    WAITING_TIME: int = Field(default=5)

    # Cache
    EXPIRY_TIME_SEC: int = Field(default=60)

    # Pagination depends
    PAGINATION_LOW_LIMIT: int = Field(default=1)
    PAGINATION_HIGH_LIMIT: int = Field(default=10)

    @property
    def get_backend_app_attributes(self) -> dict[str, str | bool | None]:
        return {
            "title": self.TITLE,
            "version": self.VERSION,
            "debug": self.DEBUG,
            "description": self.DESCRIPTION,
        }

    @property
    def get_uvicorn_attributes(self) -> dict[str, str | bool | None]:
        from utils.logger_config import configurate_logging_uvicorn_console
        return {
            'host': self.WEB_HOST,
            'port': self.WEB_PORT,
            'reload': self.RELOAD,
            'log_level': self.LOGGING_LEVEL,
            'log_config': configurate_logging_uvicorn_console()
        }

    @property
    def get_db_url(self) -> str:
        return f'{self.DB_DRIVER}://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}'

    @property
    def get_redis_attributes(self) -> dict[str, str | int | bool]:
        return {
            'url': f'{self.REDIS_DRIVER}://{self.REDIS_HOST}:{self.REDIS_PORT}',
            'encoding': self.REDIS_ENCODING,
            'decode_responses': self.DECODE_RESPONSES
        }

    @property
    def get_middleware_attributes(self) -> dict[str, str | list[str]]:
        return {
            'allow_origins': self.ORIGINS,
            'allow_methods': self.ALLOW_METHODS,
            'allow_headers': self.ALLOW_HEADERS,
            'allow_credentials': self.ALLOW_CREDENTIALS,
        }

    @property
    def get_file_logging_class_attributes(self) -> dict[str, str | int]:
        return {
            'filename': self.FILE_LOGGING_FILENAME,
            'maxBytes': self.FILE_MAX_BYTES,
            'backupCount': self.FILE_BACKUP_COUNT,
            'mode': self.FILE_LOGGING_MODE
        }

    @property
    def get_file_logging_formatter_attributes(self) -> dict[str, str]:
        return {
            'fmt': self.LOGGING_FORMAT,
            'datefmt': self.LOGGING_DATEFMT
        }


settings = Settings()
