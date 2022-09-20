"""Module to access and modify configuration settings with ease."""

import os, json, aiohttp
from typing import List, Union

DISCORD_BOT_CONFIG_PATH = os.getenv("DISCORD_BOT_CONFIG_PATH")
assert (
    DISCORD_BOT_CONFIG_PATH
), "Set the DISCORD_BOT_CONFIG_PATH Environment Variable before running."
with open(DISCORD_BOT_CONFIG_PATH) as config_file:
    config = json.load(config_file)

BOT_CONFIG = config["bot"]
API_CONFIG = config["api"]

USERNAME_TO_UUID_URL = "https://api.mojang.com/users/profiles/minecraft/{}"
UUID_TO_USERNAME_URL = "https://sessionserver.mojang.com/session/minecraft/profile/{}"


async def convert_username_to_uuid(username: str) -> Union[str, None]:
    """Convert a username to a UUID, returning None if not found."""
    try:
        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=10)
        ) as session:
            async with session.get(USERNAME_TO_UUID_URL.format(username)) as response:
                data = await response.json()
                return data["id"]
    except:
        return None


async def convert_uuid_to_username(uuid: str) -> Union[str, None]:
    """Convert a UUID to a Username, returning a None if not found."""
    async with aiohttp.ClientSession() as session:
        async with session.get(UUID_TO_USERNAME_URL.format(uuid)) as response:
            data = await response.json()
            return data.get("name", "").lower()


def get_data():
    """Read and return the 'data' portion of the API Configuration."""
    with open(DISCORD_BOT_CONFIG_PATH) as config_file:
        config = json.load(config_file)
        API_CONFIG = config["api"]
        return API_CONFIG["data"]


def set_data(players: List, mode: str):
    """Update the Player List and Proxy Mode on the configuration file."""
    with open(DISCORD_BOT_CONFIG_PATH, "r") as config_file:
        config = json.load(config_file)
        config["api"]["data"] = {
            "players": list(set([player.lower() for player in players])),
            "mode": mode.lower(),
        }
    with open(DISCORD_BOT_CONFIG_PATH, "w") as config_file:
        json.dump(config, config_file, indent=4)
        API_CONFIG = config["api"]
