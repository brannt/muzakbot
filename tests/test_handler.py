from unittest import mock

import pytest
from bot.event import EventType
from muzakbot.settings import ChatSettings, HandlerStrategy, MuzakbotSettings
from muzakbot.thebot import FoundData, SongLinkHandler
from requests.exceptions import RequestException

from . import factories


@pytest.fixture
def settings():
    settings = MuzakbotSettings(token="")
    settings.chats["default"].handler_strategy = HandlerStrategy.ALL
    return settings


@pytest.fixture
def handler(bot, settings):
    return SongLinkHandler(bot, settings)


@pytest.mark.parametrize(
    ("strategy", "event_data", "expected"),
    [
        (
            HandlerStrategy.COMMAND,
            "/links https://open.spotify.com/test",
            FoundData(
                "https://open.spotify.com/test",
                "/links https://open.spotify.com/test",
            ),
        ),
        (HandlerStrategy.COMMAND, "https://open.spotify.com/test", None),
        (
            HandlerStrategy.MENTION,
            {
                "text": "https://open.spotify.com/test",
                "parts": [factories.mention(123456)],
            },
            FoundData(
                "https://open.spotify.com/test", "https://open.spotify.com/test"
            ),
        ),
        (
            HandlerStrategy.MENTION,
            {
                "text": "https://open.spotify.com/test",
                "parts": [factories.mention(123455)],
            },
            None,
        ),
        (HandlerStrategy.MENTION, "https://open.spotify.com/test", None),
        (
            HandlerStrategy.ALL,
            "https://open.spotify.com/test",
            FoundData(
                "https://open.spotify.com/test", "https://open.spotify.com/test"
            ),
        ),
        (HandlerStrategy.ALL, "https://example.com/test", None),
    ],
)
def test_handler_strategy(handler, strategy, event_data, expected):
    handler.settings.chats["default"].handler_strategy = strategy
    event = factories.event(event_data)
    assert expected == handler.check_for_data(event)


@pytest.mark.parametrize(
    ("domains", "event_data", "expected"),
    [
        (
            ["spotify"],
            "https://open.spotify.com/test",
            FoundData(
                "https://open.spotify.com/test", "https://open.spotify.com/test"
            ),
        ),
        (
            ["spotify", "youtube"],
            "Look at this cool video: youtube.com/video/dgfdfgfd \nI like it a lot",
            FoundData(
                "youtube.com/video/dgfdfgfd",
                "Look at this cool video: youtube.com/video/dgfdfgfd \nI like it a lot",
            ),
        ),
        (["youtube", "deezer"], "https://open.spotify.com/test", None),
        (["apple"], "https://example.com/test", None),
        (["yandex"], "No link in message", None),
    ],
)
def test_check_domains(handler, domains, event_data, expected):
    handler.settings.chats["default"].check_domains = domains
    event = factories.event(event_data)
    assert expected == handler.check_for_data(event)


def test_forwarded_message(handler):
    event = factories.event(
        {
            "parts": [
                factories.part(
                    "forward", message={"text": "https://open.spotify.com/test"}
                )
            ]
        }
    )
    assert FoundData(
        "https://open.spotify.com/test", "https://open.spotify.com/test"
    ) == handler.check_for_data(event)


def test_replied_message(handler):
    event = factories.event(
        {
            "parts": [
                factories.part(
                    "reply", message={"text": "https://open.spotify.com/test"}
                )
            ]
        }
    )
    assert FoundData(
        "https://open.spotify.com/test", "https://open.spotify.com/test"
    ) == handler.check_for_data(event)


def test_custom_chat_settings(handler):
    handler.settings.chats["custom"] = ChatSettings(
        limit_platforms=["amazon"],
        check_domains=["youtube.com"],
        button_row_length=10,
        handler_strategy=HandlerStrategy.ALL,
    )
    event = factories.event(
        {"text": "https://youtube.com/test", "chat": {"chatId": "custom"}}
    )
    settings = handler.get_chat_settings(event)
    assert settings.limit_platforms == ["amazon"]
    assert settings.check_domains == ["youtube.com"]
    assert settings.button_row_length == 10
    assert settings.handler_strategy == HandlerStrategy.ALL
    data = handler.check_for_data(event)
    assert data is not None
    assert data.url == "https://youtube.com/test"


def test_send_message(handler):
    event = factories.event("https://open.spotify.com/test")
    with mock.patch("muzakbot.odesli.get_links") as patched:
        patched.return_value = factories.odesli_response()
        handler(handler.bot, event)
    handler.bot.assert_last_call_kwargs(
        chat_id="test",
        text="Kid Cudi - Kitchen",
        reply_msg_id=999,
        inline_keyboard_markup=[
            [
                {
                    "text": "Apple Music",
                    "url": "https://music.apple.com/us/album/kitchen/1443108737?i=1443109064&uo=4&app=music&ls=1&at=1000lHKX",
                },
                {
                    "text": "Spotify",
                    "url": "https://open.spotify.com/track/0Jcij1eWd5bDMU5iPbxe2i",
                },
                {
                    "text": "Youtube",
                    "url": "https://www.youtube.com/watch?v=w3LJ2bDvDJs",
                },
            ]
        ],
    )


def test_limit_platforms(handler):
    handler.settings.chats["default"].limit_platforms = ["appleMusic"]
    event = factories.event("https://open.spotify.com/test")
    with mock.patch("muzakbot.odesli.get_links") as patched:
        patched.return_value = factories.odesli_response()
        handler(handler.bot, event)
    handler.bot.assert_last_call_kwargs(
        chat_id="test",
        text="Kid Cudi - Kitchen",
        reply_msg_id=999,
        inline_keyboard_markup=[
            [
                {
                    "text": "Apple Music",
                    "url": "https://music.apple.com/us/album/kitchen/1443108737?i=1443109064&uo=4&app=music&ls=1&at=1000lHKX",
                },
            ]
        ],
    )


@pytest.mark.parametrize(("event_type"), [e.value for e in EventType])
def test_event_types(handler, event_type):
    event = factories.event({}, event_type)
    with mock.patch("muzakbot.odesli.get_links") as patched:
        handler(handler.bot, event)
        patched.assert_not_called()


def test_odesli_api_error(handler):
    event = factories.event("/links https://open.spotify.com/test")
    with mock.patch("muzakbot.odesli.get_links") as patched:
        patched.side_effect = RequestException
        handler(handler.bot, event)
    handler.bot.assert_not_called()


def test_odesli_api_wrong_format(handler):
    event = factories.event("/links https://open.spotify.com/test")
    with mock.patch("muzakbot.odesli.get_links") as patched:
        patched.return_value = {}
        handler(handler.bot, event)
    handler.bot.assert_not_called()
