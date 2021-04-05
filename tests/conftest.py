from typing import Any, Mapping, Sequence

import json

import pytest


class Bot:
    uin = 123456

    def __init__(self) -> None:
        self.__calls: list[tuple[Sequence[Any], Mapping[str, Any]]] = []

    def send_text(self, *args, **kwargs):
        self.__calls.append((args, kwargs))

    def assert_not_called(self):
        assert not self.__calls

    def assert_last_call_kwargs(self, **kwargs):
        if "inline_keyboard_markup" in kwargs:
            kwargs["inline_keyboard_markup"] = json.dumps(
                kwargs["inline_keyboard_markup"]
            )
        assert self.__calls[-1][1] == kwargs


@pytest.fixture
def bot():
    return Bot()
