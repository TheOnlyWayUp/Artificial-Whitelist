"""Request Functions to talk to Proxy Server API and fetch/kick players."""

import asyncio, socket, os, json
from typing import List, Union


async def kick_player(player_uuid: str) -> Union[bool, None]:
    """Kick a player, returning a boolean success."""
    host, port = os.environ["PROXY_SERVER_API_URL"].split(":")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, int(port)))
    data = {"auth": os.environ["API_AUTH_KEY"], "action": "kick", "uuid": player_uuid}

    loop = asyncio.get_event_loop()
    await loop.sock_sendall(sock, json.dumps(data).encode())
    success = json.loads((await loop.sock_recv(sock, 1024)).decode("utf8")).get(
        "success"
    )
    return success


async def get_players() -> Union[List[str], None]:
    """Return a list of all online players, provided by the server. (No Anonymous Users)"""
    host, port = os.environ["PROXY_SERVER_API_URL"].split(":")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, int(port)))
    data = {"auth": os.environ["API_AUTH_KEY"], "action": "online"}

    loop = asyncio.get_event_loop()
    await loop.sock_sendall(sock, json.dumps(data).encode())
    resp = json.loads((await loop.sock_recv(sock, 1024)).decode("utf8"))
    if resp.get("success"):
        return resp.get("players")
    return None
