from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from aiogram.filters import CommandStart, Text

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
        video_info = video.get_video_answer(yt_video_id)
        if isinstance(video_info, str):
            await message.answer(text=video_info)
        else:
            btn_channel = InlineKeyboardButton(text=f'👤 Канал: {video_info["channel_title"]}',
                                               callback_data=f'channel {video_info["channel_id"]}')

            markup = InlineKeyboardMarkup(inline_keyboard=[[btn_channel]])

            await message.answer(text=video_info['text'], reply_markup=markup)
    except Exception as e:
        await message.answer(text=f'Произошла ошибка, сообщите о ней администратору бота:\n\n{e}', parse_mode=None)
        raise e


@router.callback_query(F.data.func(lambda data: data.startswith('video ')))
async def proces_video_cb(callback: CallbackQuery):
    try:
        yt_video_id = callback.data[6:]
        video_info = video.get_video_answer(yt_video_id)

        if isinstance(video_info, str):
            await callback.message.answer(text=video_info)

        else:
            btn_channel = InlineKeyboardButton(text=f'👤 Канал: {video_info["channel_title"]}',
                                               callback_data=f'channel {video_info["channel_id"]}')

            markup = InlineKeyboardMarkup(inline_keyboard=[[btn_channel]])

            await callback.message.answer(text=video_info['text'], reply_markup=markup)

        await callback.answer()
    except Exception as e:
        await callback.message.answer(text=f'Произошла ошибка, сообщите о ней администратору бота:\n\n{e}',
                                      parse_mode=None)
        raise e


@router.message(IsChannelLink())
async def process_channel(message: Message, yt_channel_id: str):
    try:
        channel_info = channel.get_channel_answer(yt_channel_id)
        if isinstance(channel_info, str):
            await message.answer(text=channel_info)
        else:
            video_ids = channel_info['video_ids']
            video_titles = channel_info['video_titles']

            if video_ids:
                btn_title = InlineKeyboardButton(text='Последние видео:', callback_data='0')
                buttons_vid = []
                for video_id, video_title in zip(video_ids, video_titles):
                    buttons_vid.append(
                        [InlineKeyboardButton(text=f'⚡️ {video_title}', callback_data=f'video {video_id}')])

                markup = InlineKeyboardMarkup(inline_keyboard=[[btn_title], *buttons_vid])

                await message.answer(text=channel_info['text'], reply_markup=markup)
            else:
                await message.answer(text=channel_info['text'])
    except Exception as e:
        await message.answer(text=f'Произошла ошибка, сообщите о ней администратору бота:\n\n{e}', parse_mode=None)
        raise e


@router.callback_query(F.data.func(lambda data: data.startswith('channel ')))
async def proces_channel_cb(callback: CallbackQuery):
    try:
        yt_channel_id = callback.data[8:]
        channel_info = channel.get_channel_answer(yt_channel_id)
        if isinstance(channel_info, str):
            await callback.message.answer(text=channel_info)
        else:
            video_ids = channel_info['video_ids']
            video_titles = channel_info['video_titles']

            if video_ids:
                btn_title = InlineKeyboardButton(text='Последние видео:', callback_data='0')
                buttons_vid = []
                for video_id, video_title in zip(video_ids, video_titles):
                    buttons_vid.append(
                        [InlineKeyboardButton(text=f'⚡️ {video_title}', callback_data=f'video {video_id}')])

                markup = InlineKeyboardMarkup(inline_keyboard=[[btn_title], *buttons_vid])

                await callback.message.answer(text=channel_info['text'], reply_markup=markup)
            else:
                await callback.message.answer(text=channel_info['text'])
        await callback.answer()
    except Exception as e:
        await callback.message.answer(text=f'Произошла ошибка, сообщите о ней администратору бота:\n\n{e}',
                                      parse_mode=None)
        raise e


@router.message(F.text)
async def process_unwanted_text(message: Message):
    await message.answer(text=LEXICON_RU['invalid_link'])


@router.message()
async def process_unwanted_message(message: Message):
    await message.answer(text=LEXICON_RU['not_link'])


@router.callback_query()
async def process_unwanted_cb_query(callback: CallbackQuery):
    await callback.answer()
