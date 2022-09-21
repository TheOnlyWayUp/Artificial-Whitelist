"""Proxy Server Module"""

import json, asyncio, socket, selectors, time
from threading import Thread
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict, List, Tuple, Union, cast
from rich.console import Console

from lib.parse_config import (
    # LiveOverflow Server Info
    SERVER_ADDRESS,
    SERVER_PORT,
    SERVER_MOTD,
    # Bind Info
    BIND_ADDRESS,
    BIND_PORT,
    # API Info
    PLAYER_API_BASE_URL,
    STATS_API_BASE_URL,
    API_AUTH_KEY,
    # Proxy MOTD Data
    # MAX_CONTROLLED_PLAYERS,
    MOTD,
    # Proxy Configuration Data
    get_proxy_mode,
    get_player_list,
    # username->uuid api
    convert_username_to_uuid,
    # proxy api (for kick functionality)
    PROXY_API_ADDRESS,
    PROXY_API_PORT,
)
from lib.api_handler import APIHandler
from lib.parse_packet import (
    parse_handshake_packet,
    check_if_packet_c2s_encryption_response,
    # check_if_packet_motd_packet,
)

console = Console()
API_Handler = APIHandler(
    authorization=API_AUTH_KEY,
    player_api_base_url=PLAYER_API_BASE_URL,
    stats_api_base_url=STATS_API_BASE_URL,
)

# --- Logging Connection Data --- #


class ProxyServer:
    def __init__(self):
        self.connected_players: Dict[str, str] = {}  # Username: IP Address
        self.clients: Dict[str, socket.socket] = {}  # IP Address: socket
        self.clients_to_servers: Dict[
            socket.socket, socket.socket
        ] = {}  # client_socket: server_socket

        self.sel = selectors.DefaultSelector()

        self.select = select.select([], [], [])

    def new_client(self, client: socket.socket):
        self.clients[client.getsockname()] = client
        server = socket.socket()
        server.connect((SERVER_ADDRESS, SERVER_PORT))
        self.clients_to_servers[client] = server

        self.select = select.select(
            list(self.clients_to_servers.keys())
            + list(self.clients_to_servers.values()),
            [],
            [],
        )
