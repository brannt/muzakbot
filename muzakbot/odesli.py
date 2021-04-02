import logging
from typing import Any, Optional
from urllib.parse import urljoin

import requests


logger = logging.getLogger(__name__)

API_BASE = 'https://api.song.link/v1-alpha.1/'


def get_links(url: str, user_country: Optional[str] = 'RU', key: Optional[str] = None) -> Any:
    params = {'url': url}
    if user_country:
        params['user_country'] = user_country
    if key:
        params['key'] = key
    response = requests.get(urljoin(API_BASE, 'links'), params=params)
    response.raise_for_status()
    return response.json()
