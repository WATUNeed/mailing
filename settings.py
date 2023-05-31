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

    # File logging settings.
    FILE_LOGGING_LEVEL: int = Field(logging.INFO)
    FILE_LOGGING_FILENAME: str = Field("logs/log")
    FILE_LOGGING_FORMAT: str = Field("%(asctime)s [%(levelname)s]: %(message)s")
    FILE_LOGGING_DATEFMT: str = Field("%Y-%m-%d %H:%M:%S")
    FILE_LOGGING_FILEMODE: str = Field('a+')

    # External mailing API settings.
    MAILING_API_URL: str = Field(default='https://probe.fbrq.cloud/v1/send/1')
    MAILING_API_HEADERS: dict = Field(default={
        'accept': 'application/json',
        'Authorization': f'Bearer {os.getenv("AUTH_TOKEN")}',
        'Content-Type': 'application/json',
    })
    MAILING_OFFSET_SEC: int = Field(default=5)
    TIMEOUT: int = Field(default=20)
    LATEST_QUEUE_DATE: datetime = Field(default=get_current_date())
    WAITING_TIME: int = 5

    @property
    def get_backend_app_attributes(self) -> dict[str, str | bool | None]:
        return {
            "title": self.TITLE,
            "version": self.VERSION,
            "debug": self.DEBUG,
            "description": self.DESCRIPTION,
        }

    @property
    def get_uvicorn_app_attributes(self) -> dict[str, str | bool | None]:
        return {
            'host': self.WEB_HOST,
            'port': self.WEB_PORT,
            'reload': self.RELOAD,
            'log_level': self.LOGGING_LEVEL
        }

    @property
    def get_db_url(self) -> str:
        return f'{self.DB_DRIVER}://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}'

    @property
    def get_file_logging_attributes(self) -> dict[str, int | str]:
        return {
            'level': self.FILE_LOGGING_LEVEL,
            'filename': self.FILE_LOGGING_FILENAME,
            'format': self.FILE_LOGGING_FORMAT,
            'datefmt': self.FILE_LOGGING_DATEFMT,
            'filemode': self.FILE_LOGGING_FILEMODE
        }


settings = Settings()
