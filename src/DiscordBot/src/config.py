import os, json
from typing import List

DISCORD_BOT_CONFIG_PATH = os.getenv("DISCORD_BOT_CONFIG_PATH")
assert (
    DISCORD_BOT_CONFIG_PATH
), "Set the DISCORD_BOT_CONFIG_PATH Environment Variable before running."
with open(DISCORD_BOT_CONFIG_PATH) as config_file:
    config = json.load(config_file)

BOT_CONFIG = config['bot']
API_CONFIG = config['api']

def get_data():
    with open(DISCORD_BOT_CONFIG_PATH) as config_file:
        config = json.load(config_file)
        API_CONFIG = config['api']
        return API_CONFIG['data']

def set_data(players: List, mode: str):
    with open(DISCORD_BOT_CONFIG_PATH, 'r+') as config_file:
        config = json.load(config_file)
        config['api']['data'] = {
            "players": players,
            "mode": mode
        }
        json.dump(config, config_file)
        API_CONFIG = config['api']
        