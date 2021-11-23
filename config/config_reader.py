import configparser
from dataclasses import dataclass


@dataclass
class WsBot:
    token: str


@dataclass
class Config:
    ws_bot: WsBot


def load_config(path: str):
    config = configparser.ConfigParser()
    config.read(path)

    ws_bot = config['ws_bot']

    return Config(
        ws_bot=WsBot(
            token=ws_bot["token"]
        )
    )
