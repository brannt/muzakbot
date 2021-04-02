from typing import Any, Union

from bot.event import Event, EventType
from pydantic.utils import deep_update


def event(event_data: Union[str, dict[str, Any]], event_type: EventType = EventType.NEW_MESSAGE) -> Event:
    default = {'chat': {'chatId': 'test'}, 'from': 'someone@mail.ru', 'msgId': 999}
    if isinstance(event_data, str):
        # for simple cases
        default['text'] = event_data
    else:
        default = deep_update(default, event_data)
    return Event(event_type, default)


def part(type: str, **payload: Any) -> dict[str, Any]:
    return {'type': type, 'payload': payload}


def mention(user_id: int) -> dict[str, Any]:
    return part('mention', userId=user_id)


def odesli_response() -> dict:
    return {
        "entityUniqueId": "ITUNES_SONG::1443109064",
        "userCountry": "US",
        "pageUrl": "https://song.link/us/i/1443109064",
        "entitiesByUniqueId": {
            "ITUNES_SONG::1443109064": {
                "id": "1443109064",
                "type": "song",
                "title": "Kitchen",
                "artistName": "Kid Cudi",
                "thumbnailUrl": "https://is4-ssl.mzstatic.com/image/thumb/Music118/v4/ac/2c/60/ac2c60ad-14c3-a8b2-d962-dc08de2da546/source/512x512bb.jpg",
                "thumbnailWidth": 512,
                "thumbnailHeight": 512,
                "apiProvider": "itunes",
                "platforms": [
                    "appleMusic",
                    "itunes"
                ]
            },
        },
        "linksByPlatform": {
            "appleMusic": {
                "url": "https://music.apple.com/us/album/kitchen/1443108737?i=1443109064&uo=4&app=music&ls=1&at=1000lHKX",
                "nativeAppUriMobile": "music://music.apple.com/us/album/kitchen/1443108737?i=1443109064&uo=4&app=music&ls=1&at=1000lHKX",
                "nativeAppUriDesktop": "itms://music.apple.com/us/album/kitchen/1443108737?i=1443109064&uo=4&app=music&ls=1&at=1000lHKX",
                "entityUniqueId": "ITUNES_SONG::1443109064"
            },
            "spotify": {
                "url": "https://open.spotify.com/track/0Jcij1eWd5bDMU5iPbxe2i",
                "nativeAppUriDesktop": "spotify:track:0Jcij1eWd5bDMU5iPbxe2i",
                "entityUniqueId": "SPOTIFY_SONG::0Jcij1eWd5bDMU5iPbxe2i"
            },
            "youtube": {
                "url": "https://www.youtube.com/watch?v=w3LJ2bDvDJs",
                "entityUniqueId": "YOUTUBE_VIDEO::w3LJ2bDvDJs"
            }
        }
    }
