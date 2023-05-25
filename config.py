from dataclasses import dataclass
from environs import Env


@dataclass
class YtApiKey:
    key: str


@dataclass
class TgBot:
    token: str
    admin_id: int


@dataclass
class Config:
    tg_bot: TgBot
    yt_api_key: YtApiKey


env = Env()
env.read_env()
print('загружаю в окружение переменные из файла')
config = Config(tg_bot=TgBot(token=env('TG_BOT_TOKEN'), admin_id=env('ADMIN_ID')),
                yt_api_key=env('YT_API_KEY'))
