"""Proxy Server Module"""

import json, asyncio, socket, select, time
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

CONNECTIONS: Dict[str, socket.socket] = {}  # Client ip_address: socket
CONNECTED_PLAYERS: Dict[str, str] = {}  # Client UUID: ip_address


def log_connection(socket: socket.socket, ip_address: Any):
    """A silent function to store connections as IP Addresses to sockets."""
    CONNECTIONS[ip_address] = socket
    return True


def log_player_connection(username: str, ip_address: Any):
    """A silent function to store connections as UUIDs to IP Addresses."""
    uuid = convert_username_to_uuid(username)
    if not uuid:
        return
    uuid = cast(str, uuid)
    CONNECTED_PLAYERS[uuid] = ip_address
    return True


def kick_player(uuid: str) -> Union[socket.socket, None]:
    """A silent function to kick a player from the server.
    This is done by removing their record in the CONNECTED_PLAYERS Dictionary, which is checked by the proxy."""
    try:
        return CONNECTIONS.pop(CONNECTED_PLAYERS.pop(uuid))
    except:
        return None


# --- Binding to Serve Address --- #

listener = socket.socket()
listener.bind((BIND_ADDRESS, BIND_PORT))
listener.listen(1)


# --- Connection Handler --- #


async def handle_connection(client: socket.socket, caddr: Tuple):
    """Connection Handler. This function is called in a newly created thread when a connection is accepted."""
    # https://motoma.io/using-python-to-be-the-man-in-the-middle/

    server = socket.socket()
    server.connect((SERVER_ADDRESS, SERVER_PORT))

    running = True
    encryption_started = False
    username = ""
    uuid = ""
    fill_in_on_leave = False
    completed_check = False
    motd_sent = False

    while running:
        try:
            ready_to_read = select.select([client, server], [], [])[0]

            if uuid:
                if uuid not in CONNECTED_PLAYERS:
                    running = False

            if client in ready_to_read:
                buf = client.recv(32767)

                if len(buf) == 0:
                    running = False

                if not completed_check:
                    if check_if_packet_c2s_encryption_response(buf):
                        # If encryption has started
                        encryption_started = True

                        proxy_mode = await get_proxy_mode()
                        uuid_list = await get_player_list()

                        console.log(proxy_mode, uuid_list, username)

                        if username:
                            uuid = convert_username_to_uuid(username)
                            if not uuid:
                                running = False
                                continue
                            uuid = cast(str, uuid)

                            log_player_connection(username, caddr)
                            player_in_list = False

                            for _uuid in uuid_list:
                                if uuid == _uuid:
                                    player_in_list = True
                                    break

                            uuid = cast(str, uuid)

                            if proxy_mode == "blacklist" and player_in_list:
                                # if the user is blacklisted
                                running = False

                            elif proxy_mode == "whitelist" and player_in_list:
                                # if the user is whitelisted
                                await API_Handler.sit_out(
                                    username, CONNECTED_PLAYERS[uuid]
                                )
                                time.sleep(3)
                                fill_in_on_leave = True

                            elif proxy_mode == "whitelist" and not player_in_list:
                                # if the user is not whitelisted
                                running = False

                            elif proxy_mode == "blacklist" and not player_in_list:
                                # if user not blacklisted
                                await API_Handler.sit_out(
                                    username, CONNECTED_PLAYERS[uuid]
                                )
                                time.sleep(3)
                                fill_in_on_leave = True

                            else:
                                running = False  # Edge Case

                            completed_check = True

                    elif not username:
                        # if not encrypted and username hasn't been grabbed
                        usrn = parse_handshake_packet(buf).get("username")

                        if usrn:
                            # if username was grabbed
                            username = usrn

                server.send(buf)

            if server in ready_to_read and running:
                buf = server.recv(32767)
                if len(buf) == 0:
                    running = False

                client.send(buf)

        except Exception:
            console.print_exception(show_locals=True)
            pass

    try:
        client.close()
    except:
        pass

    try:
        server.close()
    except:
        pass

    assert type(uuid) is str

    if fill_in_on_leave:
        await API_Handler.fill_in(username, CONNECTED_PLAYERS[uuid])

    if uuid:
        CONNECTIONS.pop(CONNECTED_PLAYERS.pop(uuid))
    else:
        pass


# --- Proxy API (for kick functionality) --- #


class HandleProxyAPI(asyncio.Protocol):
    def connection_made(self, transport):
        self.transport = transport

    def data_received(self, data):
        message = data.decode()
        try:
            data = json.loads(message)  # ex: {"auth": "", "action": "kick", "uuid": ""}

            if data["auth"] != API_AUTH_KEY:
                raise Exception("403")
            if data["action"] not in ["kick", "online"]:
                raise Exception("422")

            if data["action"] == "kick":
                try:
                    kick_player(data["uuid"])
                    self.transport.write(json.dumps({"success": True}).encode())
                except Exception:
                    self.transport.write(json.dumps({"success": False}).encode())
                    raise Exception("500")
            elif data["action"] == "online":
                try:
                    self.transport.write(
                        json.dumps(
                            {"success": True, "players": list(CONNECTED_PLAYERS.keys())}
                        ).encode()
                    )
                except Exception:
                    self.transport.write(
                        json.dumps({"success": False, "players": []}).encode()
                    )

        except:
            self.transport.write(json.dumps({"success": False}).encode())

        self.transport.close()


async def handle_proxy_api():
    """Proxy API Runner.
    Handles actions, validation and responses for the Proxy API."""
    loop = asyncio.get_running_loop()

    server = await loop.create_server(
        lambda: HandleProxyAPI(), PROXY_API_ADDRESS, PROXY_API_PORT
    )

    async with server:
        await server.serve_forever()


def run_proxy_api():
    asyncio.run(handle_proxy_api())


# --- #


async def run_proxy_server():
    """Proxy Server Runner."""

    async def run_and_clean():
        asyncio.ensure_future(handle_connection(*lner))
        CONNECTIONS.pop(lner[1])

    while True:
        lner = listener.accept()
        log_connection(*lner)
        await asyncio.ensure_future(run_and_clean())


# --- #


async def main():
    t = Thread(target=run_proxy_api)
    t.setDaemon(True)
    t.start()

    await asyncio.ensure_future(run_proxy_server())


# --- Running --- #

if __name__ == "__main__":
    console.log("[App] - Starting")
    asyncio.run(main())

    # ---- #
