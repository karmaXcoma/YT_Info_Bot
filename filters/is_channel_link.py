from aiogram.filters import BaseFilter
from aiogram.types import Message

from utils import get_channel_id_from_username


class IsChannelLink(BaseFilter):
    async def __call__(self, message: Message) -> bool | dict[str: str]:
        link = message.text

        if not link:
            return False

        if link[0] == '@':
            for c in link[1:]:
                if not c.isalnum() and c not in '-_.':
                    return False
            return {'yt_channel_id': get_channel_id_from_username(link)}

        if '@' in link:
            link = link.split('@')[-1]
            link = link.split('/')[0]
            for c in link:
                if not c.isalnum() and c not in '-_.':
                    return False
            return {'yt_channel_id': get_channel_id_from_username(link)}

        if 'youtube.com/user' in link:
            link = link.split('youtube.com/user/')[-1]
            link = link.split('/')[0]
            for c in link:
                if not c.isalnum() and c not in '-_.':
                    return False
            return {'yt_channel_id': get_channel_id_from_username(link)}

        link = link.split('youtube.com/channel/')[-1]
        link = link.split('/')[0]
        for c in link:
            if not c.isalnum() and c not in '-_.':
                return False

        return {'yt_channel_id': link}
