import requests
from datetime import datetime
from typing import Union

from utils import truncate_text
from lexicon import LEXICON_RU
from config import config

YT_API_KEY = config.yt_api_key

YT_CHANNEL_API_URL = 'https://www.googleapis.com/youtube/v3/channels'
YT_PLAYLIST_ITEMS_API_URL = 'https://youtube.googleapis.com/youtube/v3/playlistItems'

YT_TOPICS_ID = {'/m/04rlf': 'Music',
                '/m/05fw6t': 'Children\'s music',
                '/m/02mscn': 'Christian music',
                '/m/0ggq0m': 'Classical music',
                '/m/01lyv': 'Country',
                '/m/02lkt': 'Electronic music',
                '/m/0glt670': 'Hip hop music',
                '/m/05rwpb': 'Independent music',
                '/m/03_d0': 'Jazz',
                '/m/028sqc': 'Music of Asia',
                '/m/0g293': 'Music of Latin America',
                '/m/064t9': 'Pop music',
                '/m/06cqb': 'Reggae',
                '/m/06j6l': 'Rhythm and blues',
                '/m/06by7': 'Rock music',
                '/m/0gywn': 'Soul music',
                '/m/0bzvm2': 'Gaming',
                '/m/025zzc': 'Action game',
                '/m/02ntfj': 'Action-adventure game',
                '/m/0b1vjn': 'Casual game',
                '/m/02hygl': 'Music video game',
                '/m/04q1x3q': 'Puzzle video game',
                '/m/01sjng': 'Racing video game',
                '/m/0403l3g': 'Role-playing video game',
                '/m/021bp2': 'Simulation video game',
                '/m/022dc6': 'Sports game',
                '/m/03hf_rm': 'Strategy video game',
                '/m/06ntj': 'Sports',
                '/m/0jm_': 'American football',
                '/m/018jz': 'Baseball',
                '/m/018w8': 'Basketball',
                '/m/01cgz': 'Boxing',
                '/m/09xp_': 'Cricket',
                '/m/02vx4': 'Football',
                '/m/037hz': 'Golf',
                '/m/03tmr': 'Ice hockey',
                '/m/01h7lh': 'Mixed martial arts',
                '/m/0410tth': 'Motorsport',
                '/m/066wd': 'Professional wrestling',
                '/m/07bs0': 'Tennis',
                '/m/07_53': 'Volleyball',
                '/m/02jjt': 'Entertainment',
                '/m/095bb': 'Animated cartoon',
                '/m/09kqc': 'Humor',
                '/m/02vxn': 'Movies',
                '/m/05qjc': 'Performing arts',
                '/m/019_rr': 'Lifestyle',
                '/m/032tl': 'Fashion',
                '/m/027x7n': 'Fitness',
                '/m/02wbm': 'Food',
                '/m/0kt51': 'Health',
                '/m/03glg': 'Hobby',
                '/m/068hy': 'Pets',
                '/m/041xxh': 'Physical attractiveness [Beauty]',
                '/m/07c1v': 'Technology',
                '/m/07bxq': 'Tourism',
                '/m/07yv9': 'Vehicles',
                '/m/01k8wb': 'Knowledge',
                '/m/098wr': 'Society'}


def get_last_videos(uploads: str, max_results: int = 3) -> Union[list[dict], False]:
    max_results = min(max_results, 50)
    r_videos = requests.get(
        url=YT_PLAYLIST_ITEMS_API_URL,
        params={
            'part': 'snippet,contentDetails',
            'playlistId': uploads,
            'maxResults': max_results,
            'key': YT_API_KEY
        },
        timeout=7)

    r_videos = r_videos.json()

    if 'items' not in r_videos:
        return []

    return r_videos['items']


def get_last_videos_text(last_videos: list[dict]) -> str:
    if not last_videos:
        return ''

    last_videos_title = '✨ <b>последние видео:</b>\n'
    last_videos_units = []

    for video in last_videos:
        video_title = truncate_text(video['snippet']['title'], 45)
        last_videos_units.append(
            f'📆 {datetime.fromisoformat(video["contentDetails"]["videoPublishedAt"]).strftime("%d.%m.%Y")} '
            f'<a href="youtube.com/watch?v={video["contentDetails"]["videoId"]}">{video_title}</a>\n'
        )

    return f"{last_videos_title}{''.join(last_videos_units)}\n"


def get_additional_info_text(link: str) -> str:
    r = requests.get(url=f'https://{link}')

    monetization = r.text[(monet_pos := r.text.find('is_monetization_enabled","value":"') + 34):monet_pos + 4]
    monetization = True if monetization == 'true' else False

    verified_channel = True if r.text.find('BADGE_STYLE_TYPE_VERIFIED') != -1 else False

    verified_artist = True if r.text.find('OFFICIAL_ARTIST_BADGE') != -1 else False

    additional_info_text = (f'<b>💸 монетизация:</b> <code>{"да" if monetization else "нет"}</code>\n'
                            f'<b>✅ верификация:</b> <code>{"да" if verified_channel else "нет"}</code>\n'
                            f'<b>🎵 канал исполнителя:</b> <code>{"да" if verified_artist else "нет"}</code>\n\n')

    return additional_info_text


def get_channel_properties(channel_id: str) -> bool | dict:
    r_channel = requests.get(
        url=YT_CHANNEL_API_URL,
        params={
            'part': 'snippet,statistics,topicDetails,contentDetails',
            'id': channel_id,
            'key': YT_API_KEY
        },
        timeout=7)

    if r_channel.status_code != 200:
        return False

    r_channel = r_channel.json()
    if 'items' not in r_channel:
        return False

    channel = r_channel['items'][0]

    channel_properties = {
        'title': channel['snippet']['title'],
        'creation_date': datetime.fromisoformat(channel['snippet']['publishedAt']).strftime('%d.%m.%Y'),
        'profile_picture': list(channel['snippet']['thumbnails'].values())[-1]['url'],
        'view_count': f"{int(channel['statistics']['viewCount']):,}".replace(',', ' '),
        'subscriber_count': f"{int(channel['statistics']['subscriberCount']):,}".replace(',', ' '),
        'video_count': f"{int(channel['statistics']['videoCount']):,}".replace(',', ' '),
        'link': f"youtube.com/{channel['snippet']['customUrl']}",
        'uploads': channel['contentDetails']['relatedPlaylists']['uploads'],
        'topics': '',
        'description': '',
        'country': ''
    }

    if 'topicDetails' in channel and channel['topicDetails']:
        topics_list = ', '.join([YT_TOPICS_ID.get(topic, '') for topic in channel['topicDetails']['topicIds']])
        channel_properties['topics'] = f"📂 <b>категории:</b> <code>{topics_list}</code>\n"
    if channel['snippet']['description']:
        channel_description = channel['snippet']['description'].replace('<', '&lt;').replace('>', '&gt;').replace('&',
                                                                                                                  '&amp;')
        channel_properties['description'] = f"📄 <b>описание канала:</b> \n\n {channel_description}"
    if 'country' in channel['snippet']:
        channel_properties['country'] = f"🌐 <b>страна:</b> <code>{channel['snippet']['country']}</code>\n"

    return channel_properties


def get_channel_info(channel_properties: dict) -> bool | dict:
    if not channel_properties:
        return False

    last_videos = get_last_videos(uploads=channel_properties['uploads'])

    last_videos_ids = []
    last_videos_titles = []
    for video in last_videos:
        last_videos_ids.append(video['contentDetails']['videoId'])
        last_videos_titles.append(video['snippet']['title'])
    last_videos_text = get_last_videos_text(last_videos=last_videos)

    additional_info_text = get_additional_info_text(link=channel_properties['link'])

    channel_text = (f"👤 <code>{channel_properties['title']}</code>\n\n"
                    f"<b>📅 дата создания канала:</b> <code>{channel_properties['creation_date']}</code>\n\n"
                    f"👥 <b>подписчиков:</b> <code>{channel_properties['subscriber_count']}</code>\n"
                    f"👁 <b>просмотров:</b> <code>{channel_properties['view_count']}</code>\n"
                    f"🎞 <b>видео:</b> <code>{channel_properties['video_count']}</code>\n\n"
                    f"{additional_info_text}"
                    f"🔗 <b>ссылка:</b> {channel_properties['link']}\n\n"
                    f"{last_videos_text}"
                    f"{channel_properties['country']}"
                    f"{channel_properties['topics']}"
                    f"\n🖼 <b>аватарка:</b> {channel_properties['profile_picture']}\n\n"
                    f"{channel_properties['description']}")

    return {'text': truncate_text(channel_text, 3000),
            'video_ids': last_videos_ids,
            'video_titles': last_videos_titles}


def get_channel_answer(yt_channel_id: str):
    channel_info = get_channel_info(get_channel_properties(yt_channel_id))
    return channel_info or LEXICON_RU['not_found_channel']
