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

    # External mailing API settings.
    MAILING_API_URL: str = Field(default='https://probe.fbrq.cloud/v1/send/1')
    MAILING_API_HEADERS: dict = Field(default={
        'accept': 'application/json',
        'Authorization': f'Bearer {os.getenv("AUTH_TOKEN")}',
        'Content-Type': 'application/json',
    })
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
        }

    @property
    def get_db_url(self) -> str:
        return f'{self.DB_DRIVER}://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}'


settings = Settings()
