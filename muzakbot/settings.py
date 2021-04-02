from enum import Enum
import logging
from typing import Optional

from pydantic import BaseModel, BaseSettings, AnyHttpUrl


ENV_PREFIX = 'MUZAKBOT_'


class HandlerStrategy(Enum):
    ALL = 'all'
    MENTION = 'mention'
    COMMAND = 'command'


class ChatSettings(BaseModel):
    limit_platforms: Optional[list[str]]
    check_domains: list[str]
    button_row_length: int
    handler_strategy: HandlerStrategy


class MuzakbotSettings(BaseSettings):
    chats: dict[str, ChatSettings] = {
        'default': ChatSettings(button_row_length=3, handler_strategy=HandlerStrategy.COMMAND, check_domains=['spotify', 'deezer', 'yandex', 'apple'])
    }
    token: str
    log_level: int = logging.INFO
    odesli_api_key: Optional[str] = None
    api_url_base: Optional[AnyHttpUrl] = None

    class Config:
        env_prefix = ENV_PREFIX

        @classmethod
        def customise_sources(
            cls,
            init_settings,
            env_settings,
            file_secret_settings,
        ):
            return (
                init_settings,
                env_settings,
                file_secret_settings,
            )
