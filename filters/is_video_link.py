from aiogram.filters import BaseFilter
from aiogram.types import Message


class IsVideoLink(BaseFilter):
    async def __call__(self, message: Message) -> bool | dict[str: str]:
        link = message.text
        if not link:
            return False
        if len(link) != 11:
            link = link.split('watch?v=')[-1]
            link = link.split('&')[0]
        if len(link) != 11:
            link = link.split('youtu.be/')[-1]
            link = link.split('&')[0]
        if len(link) != 11:
            return False
        for c in link:
            if not c.isalnum() and c not in '-_':
                return False
        return {'yt_video_id': link}
