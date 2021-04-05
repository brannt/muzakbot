from typing import Iterable, TypeVar

import re
from itertools import chain, islice


def uncamelize(string: str) -> str:
    hd, *tl = re.sub(
        "([A-Z][a-z]+)", r" \1", re.sub("([A-Z]+)", r" \1", string)
    ).split()
    return " ".join(chain([hd.capitalize(), *tl]))


T = TypeVar("T")


def chunks(iterable: Iterable[T], n: int) -> Iterable[list[T]]:
    it = iter(iterable)
    while True:
        chunk = list(islice(it, n))
        if not chunk:
            break
        yield chunk
