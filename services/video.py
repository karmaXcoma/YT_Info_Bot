import requests
from datetime import datetime, time, timezone, timedelta
from isodate import parse_duration

from utils import truncate_text
from lexicon import LEXICON_RU
from config import config

YT_API_KEY = config.yt_api_key

YT_VIDEO_API_URL = 'https://www.googleapis.com/youtube/v3/videos'

YT_CATEGORIES_ID = {1: 'Film & Animation',
                    2: 'Autos & Vehicles',
                    10: 'Music',
                    15: 'Pets & Animals',
                    17: 'Sports',
                    18: 'Short Movies',
                    19: 'Travel & Events',
                    20: 'Gaming',
                    21: 'Videoblogging',
                    22: 'People & Blogs',
                    23: 'Comedy',
                    24: 'Entertainment',
                    25: 'News & Politics',
                    26: 'Howto & Style',
                    27: 'Education',
                    28: 'Science & Technology',
                    29: 'Nonprofits & Activism',
                    30: 'Movies',
                    31: 'Anime/Animation',
                    32: 'Action/Adventure',
                    33: 'Classics',
                    34: 'Comedy',
                    35: 'Documentary',
                    36: 'Drama',
                    37: 'Family',
                    38: 'Foreign',
                    39: 'Horror',
                    40: 'Sci-Fi/Fantasy',
                    41: 'Thriller',
                    42: 'Shorts',
                    43: 'Shows',
                    44: 'Trailers'}


def get_video_duration(duration) -> str:
    if isinstance(duration, str):
        seconds = parse_duration(duration).total_seconds()
    else:
        seconds = duration
    if seconds > 86400:
        return 'более 24:00:00'
    h, s = divmod(seconds, 3600)
    m, s = divmod(s, 60)
    duration_obj = time(int(h), int(m), int(s))
    return duration_obj.strftime('%H:%M:%S')


def get_video_properties(video_id: str) -> bool | dict:
    r_video = requests.get(
        url=YT_VIDEO_API_URL,
        params={
            'part': 'contentDetails,id,liveStreamingDetails,snippet,statistics',
            'id': video_id,
            'key': YT_API_KEY
        },
        timeout=7)

    if r_video.status_code != 200:
        return False

    items = r_video.json()['items']
    if not items:
        return False

    video = items[0]

    video_properties = {
        'title': video['snippet']['title'],
        'video_id': video['id'],
        'channel_id': video['snippet']['channelId'],
        'channel_title': video['snippet']['channelTitle'],
        'view_count': f"{int(video['statistics']['viewCount']):,}".replace(',', ' '),
        'like_count': f"{int(video['statistics']['likeCount']):,}".replace(',', ' '),
        'comment_count': f"{int(video['statistics'].get('commentCount', 0)):,}".replace(',', ' '),
        'preview': list(video['snippet']['thumbnails'].values())[-1]['url'],
        'tags': f"<code>{', '.join(video['snippet']['tags'])}</code>" if 'tags' in video['snippet'] else 'не указаны',
        'is_live': 'да' if video['snippet']['liveBroadcastContent'] == 'live' else 'нет',
        'pub_date': datetime.fromisoformat(video['snippet']['publishedAt']).strftime('%d.%m.%Y %H:%M:%S'),
        'duration': f"🕐 <b>длительность:</b> <code>{get_video_duration(video['contentDetails']['duration'])}</code>\n\n",
        'audio_lang': video['snippet'].get('defaultAudioLanguage', None) or 'не указан',
        'category': YT_CATEGORIES_ID.get(int(video['snippet']['categoryId']), 'не указана'),
        'description': video['snippet']['description'].replace('<', '&lt;').replace('>', '&gt;').replace('&', '&amp;'),
        'start_time': '',
        'cur_duration': '',
        'cur_viewers': ''
    }

    if video_properties['is_live'] == 'да':
        video_properties['duration'] = ''

        start_time = datetime.fromisoformat(video['liveStreamingDetails']['actualStartTime'])
        video_properties['start_time'] = f"🕐 <b>начало:</b> <code>{(start_time + timedelta(hours=3)).strftime('%d.%m.%Y %H:%M:%S')} МСК</code>\n"

        cur_duration = datetime.now(tz=timezone.utc) - start_time
        video_properties['cur_duration'] = f"⏳ <b>идет:</b> <code>{get_video_duration(cur_duration.total_seconds())}</code>\n"

        video_properties['cur_viewers'] = f"👥 <b>зрителей:</b> <code>{int(video['liveStreamingDetails']['concurrentViewers']):,}</code>\n\n".replace(',', ' ')

    return video_properties


def get_video_info(video_properties: dict) -> bool | dict[str, str]:
    if not video_properties:
        return False

    video_text = (f"⚡️ <code>{video_properties['title']}</code>\n\n"
                  f"📅 <b>дата публикации:</b> <code>{video_properties['pub_date']}</code>\n"
                  f"🔗 <b>короткая ссылка:</b> https://youtu.be/{video_properties['video_id']}\n\n"
                  f"👤 <b>канал:</b> <a href='youtube.com/channel/{video_properties['channel_id']}'>{video_properties['channel_title']}</a>\n"
                  f"🆔 <b>id канала:</b> <code>{video_properties['channel_id']}</code>\n\n"
                  f"👁 <b>просмотров:</b> <code>{video_properties['view_count']}</code>\n"
                  f"👍 <b>лайков:</b> <code>{video_properties['like_count']}</code>\n"
                  f"💬 <b>комментариев:</b> <code>{video_properties['comment_count']}</code>\n\n"
                  f"🖼 <b>превью:</b> {video_properties['preview']}\n\n"
                  f"🏷 <b>теги:</b> {video_properties['tags']}\n\n"
                  f"📺 <b>стрим:</b> <code>{video_properties['is_live']}</code>\n"
                  f"{video_properties['start_time']}"
                  f"{video_properties['cur_duration']}"
                  f"{video_properties['cur_viewers']}"
                  f"{video_properties['duration']}"
                  f"🌐 <b>язык аудио:</b> <code>{video_properties['audio_lang']}</code>\n"
                  f"📂 <b>категория:</b> <code>{video_properties['category']}</code>\n\n"
                  f"📄 <b>описание:</b>\n\n{video_properties['description']}")

    return {'text': truncate_text(video_text, 3000),
            'channel_id': video_properties['channel_id'],
            'channel_title': video_properties['channel_title']}


def get_video_answer(yt_video_id: str):
    video_info = get_video_info(get_video_properties(yt_video_id))

    return video_info or LEXICON_RU['not_found_video']
