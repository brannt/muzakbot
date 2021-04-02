import re
import json
import logging
import weakref
from dataclasses import dataclass
from typing import Any, Optional

from bot.bot import Bot
from bot.event import Event
from bot.handler import MessageHandler
from requests.exceptions import RequestException

from muzakbot import odesli
from muzakbot.settings import ChatSettings, HandlerStrategy, MuzakbotSettings
from muzakbot.utils import uncamelize, chunks

logger = logging.getLogger(__name__)

RE_PREFIX = r"""
    \b(\w+://)? # schema
    [\w.]* # TLD
"""

RE_SUFFIX = r"\S+"


@dataclass
class FoundData:
    url: str
    text: str


class SongLinkHandler:
    links_command = '/links'

    def __init__(self, bot: Bot, settings: MuzakbotSettings) -> None:
        self.bot = weakref.proxy(bot)
        self.settings = settings

    def __call__(self, bot: Bot, event: Event) -> None:
        if data := self.check_for_data(event):
            self.handle(event, data)

    def build_url_re(self, domains: list[str]) -> re.Pattern:
        domains_re = f"({'|'.join(domains)})"

        return re.compile(RE_PREFIX + domains_re + RE_SUFFIX, re.VERBOSE)

    def get_chat_settings(self, event: Event) -> ChatSettings:
        return self.settings.chats.get(event.from_chat) or self.settings.chats['default']

    def get_text(self, event: Event) -> Optional[str]:
        if 'text' in event.data:
            return event.data['text']
        if 'parts' in event.data:
            return next(
                (p['payload']['message'].get('text') for p in event.data['parts'] if 'message' in p['payload']),
                None
            )
        return None

    def has_mention(self, event: Event) -> bool:
        return 'parts' in event.data and any(p['type'] == 'mention' and p['payload']['userId'] == self.bot.uin for p in event.data['parts'])

    def check_for_data(self, event: Event) -> Optional[FoundData]:
        text = self.get_text(event)
        if not text:
            return None
        settings = self.get_chat_settings(event)
        if settings.handler_strategy == HandlerStrategy.MENTION and not self.has_mention(event):
            return None
        if settings.handler_strategy == HandlerStrategy.COMMAND and self.links_command not in text:
            return None
        url = self.build_url_re(settings.check_domains).search(text)
        if url is None:
            return None
        return FoundData(url.group(0), text)

    def handle(self, event: Event, data: FoundData) -> None:
        logger.info('Got event %s', event)
        settings = self.get_chat_settings(event)

        try:
            resp = odesli.get_links(data.url)
            entity_data = resp['entitiesByUniqueId'][resp['entityUniqueId']]

            links = resp['linksByPlatform'].items()
        except (RequestException, KeyError) as e:
            logger.exception('%s parsing Odesli response\n Arguments: %r', e, e.args)
            return
        if settings.limit_platforms is not None:
            links = ((k, v) for k, v in links if k in settings.limit_platforms)

        keyboard = self.get_keyboard(settings, links)

        self.bot.send_text(
            chat_id=event.from_chat,
            text=' - '.join((entity_data.get('artistName', ''), entity_data.get('title', ''))),
            reply_msg_id=event.data['msgId'],
            inline_keyboard_markup=json.dumps(keyboard),
        )

    def get_keyboard(self, settings: ChatSettings, links: tuple[str, dict]) -> list[list[dict]]:
        keyboard = [[
            {'text': uncamelize(k), 'url': v['url']} for k, v in chunk
        ] for chunk in chunks(links, settings.button_row_length)]
        return keyboard


def start_bot(settings: MuzakbotSettings) -> None:
    logger.info('Bot started')
    bot = Bot(token=settings.token, api_url_base=settings.api_url_base)
    bot.dispatcher.add_handler(MessageHandler(callback=SongLinkHandler(bot, settings)))
    bot.start_polling()
    bot.idle()
