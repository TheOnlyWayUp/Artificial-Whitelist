import os, json, requests
from typing import cast, Dict
from enum import Enum
from mcstatus import JavaServer

PROXY_CONFIG_PATH = os.getenv("PROXY_CONFIG_PATH")
assert (
    PROXY_CONFIG_PATH
), "Set the PROXY_CONFIG_PATH Environment Variable before running."
with open(PROXY_CONFIG_PATH) as config_file:
    config = json.load(config_file)

_PROXY_CONFIG = config["proxy"]

BIND_ADDRESS = _PROXY_CONFIG["bind"]["address"]
BIND_PORT = _PROXY_CONFIG["bind"]["port"]

SERVER_ADDRESS = _PROXY_CONFIG["proxy_to"]["address"]
SERVER_PORT = _PROXY_CONFIG["proxy_to"]["port"]

PLAYER_API_BASE_URL = _PROXY_CONFIG["player_api_url"]
STATS_API_BASE_URL = _PROXY_CONFIG["stats_api_url"]
CONFG_API_BASE_URL = _PROXY_CONFIG["config_api_url"]
API_AUTH_KEY = os.environ["API_AUTH_KEY"]

MAX_CONTROLLED_PLAYERS = requests.get(PLAYER_API_BASE_URL + "/maxlen").json()[
    "MAX_SIZE"
]

MOTD = "LiveOverflow Proxy"
SERVER_MOTD = cast(
    Dict, JavaServer(SERVER_ADDRESS, SERVER_PORT).status().raw.get("description", {})
).get("text", "")


class ProxyModeEnum(Enum):
    whitelist = 1
    blacklist = 2


headers = {"authorization": API_AUTH_KEY}


def get_proxy_mode():
    return requests.get(CONFG_API_BASE_URL + "/mode", headers=headers)


def get_player_list():
    return requests.get(CONFG_API_BASE_URL + "/players", headers=headers)
