from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart

from services import video, channel
from lexicon import LEXICON_RU
from filters.is_video_link import IsVideoLink
from filters.is_channel_link import IsChannelLink

router: Router = Router()


@router.message(CommandStart())
async def process_start_command(message: Message):
    await message.answer(text=LEXICON_RU['start_command'])


@router.message(IsVideoLink())
async def process_video(message: Message, yt_video_id: str):
    try:
        await message.answer(text=video.get_video_answer(yt_video_id))
    except Exception as e:
        await message.answer(text=f'Произошла ошибка, сообщите о ней администратору бота:\n\n{e}', parse_mode=None)


@router.message(IsChannelLink())
async def process_channel(message: Message, yt_channel_id: str):
    try:
        await message.answer(text=channel.get_channel_answer(yt_channel_id))
    except Exception as e:
        await message.answer(text=f'Произошла ошибка, сообщите о ней администратору бота:\n\n{e}', parse_mode=None)


@router.message(F.text)
async def process_unwanted_text(message: Message):
    await message.answer(text=LEXICON_RU['invalid_link'])


@router.message()
async def process_unwanted_message(message: Message):
    await message.answer(text=LEXICON_RU['not_link'])
