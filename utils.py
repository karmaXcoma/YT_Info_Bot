import requests


def truncate_text(text: str, max_len: int) -> str:
    if len(text) > max_len:
        return f'{text[:max_len]} …'
    return text


def get_channel_id_from_username(username: str):
    r = requests.get(
        url=f'https://www.youtube.com/{username}'
    )
    if r.status_code == 200:
        pos = r.text.find('<link rel="canonical"')
        return r.text[pos+60:pos+84]
    return False