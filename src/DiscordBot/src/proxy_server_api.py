import asyncio, socket, os, json
from typing import List, Union


async def kick_player(player_uuid: str) -> Union[bool, None]:
    host, port = os.environ["PROXY_SERVER_API_URL"].split(":")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)
    sock.connect((host, port))
    data = {"auth": os.environ["API_AUTH_KEY"], "action": "kick", "uuid": player_uuid}

    loop = asyncio.get_event_loop()
    await loop.sock_sendall(sock, json.dumps(data).encode())
    success = json.loads((await loop.sock_recv(sock, 1024)).decode("utf8")).get(
        "success"
    )
    return success


async def get_players() -> Union[List[str], None]:
    host, port = os.environ["PROXY_SERVER_API_URL"].split(":")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)
    sock.connect((host, port))
    data = {"auth": os.environ["API_AUTH_KEY"], "action": "online"}

    loop = asyncio.get_event_loop()
    await loop.sock_sendall(sock, json.dumps(data).encode())
    resp = json.loads((await loop.sock_recv(sock, 1024)).decode("utf8"))
    if resp.get("success"):
        return resp.get("players")
    return None
