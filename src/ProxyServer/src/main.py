import socket, select, time, requests
from threading import Thread
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict, List, Tuple, Union, cast
from rich.console import Console
from mcstatus import JavaServer

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
)
from lib.api_handler import APIHandler
from lib.parse_packet import (
    parse_handshake_packet,
    check_if_packet_c2s_encryption_response,
    check_if_packet_motd_packet,
)

console = Console()
API_Handler = APIHandler(
    authorization=API_AUTH_KEY,
    player_api_base_url=PLAYER_API_BASE_URL,
    stats_api_base_url=STATS_API_BASE_URL,
)

# --- Logging Connection Data --- #

CONNECTIONS: Dict[str, socket.socket] = {}  # Client ip_address: socket
CONNECTED_PLAYERS: Dict[str, str] = {}  # Client Username: ip_address


def log_connection(socket: socket.socket, ip_address: Any):
    CONNECTIONS[ip_address] = socket
    return True


def log_player_connection(username: str, ip_address: Any):
    CONNECTED_PLAYERS[username] = ip_address
    return True


# --- Binding to Serve Address --- #

listener = socket.socket()
listener.bind((BIND_ADDRESS, BIND_PORT))
listener.listen(1)


# --- Connection Handler --- #


def handle_connection(client: socket.socket, caddr: Tuple):
    # https://motoma.io/using-python-to-be-the-man-in-the-middle/

    server = socket.socket()
    server.connect((SERVER_ADDRESS, SERVER_PORT))

    running = True
    encryption_started = False
    username = ""
    fill_in_on_leave = False
    completed_check = False
    motd_sent = False

    proxy_mode = get_proxy_mode()
    player_list = get_player_list()

    while running:
        try:
            rlist = select.select([client, server], [], [])[0]

            if client in rlist:
                buf = client.recv(32767)
                if len(buf) == 0:
                    running = False

                if not completed_check:
                    if check_if_packet_c2s_encryption_response(buf):
                        # If encryption has started

                        if username:
                            log_player_connection(username, caddr)
                            # if the username has been grabbed
                            player_in_list = False

                            for player in player_list:
                                if player == username.lower():
                                    player_in_list = True
                                    break

                            if proxy_mode == "blacklist" and player_in_list:
                                # if the user is blacklisted
                                running = False

                            elif proxy_mode == "whitelist" and player_in_list:
                                # if the user is whitelisted
                                API_Handler.sit_out(
                                    username, CONNECTED_PLAYERS[username]
                                )
                                time.sleep(3)
                                fill_in_on_leave = True

                            elif proxy_mode == "whitelist" and not player_in_list:
                                # if the user is not whitelisted
                                running = False

                            elif proxy_mode == "blacklist" and not player_in_list:
                                # if user not blacklisted
                                API_Handler.sit_out(
                                    username, CONNECTED_PLAYERS[username]
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

            if server in rlist and running:
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

    if fill_in_on_leave:
        # When the user is authorized, and space is created, this cleanup condition is executed to fill in for them after they leave
        API_Handler.fill_in(username, CONNECTED_PLAYERS[username])

    try:
        CONNECTIONS.pop(
            CONNECTED_PLAYERS.pop(username)
        )  # Remove user data from connection dictionaries for cleanup
    except:
        pass


# --- Running --- #
executor = ThreadPoolExecutor(
    5
)  # make this MAX_CONTROLLED_PLAYERS when it's no longer unused by motd

if __name__ == "__main__":
    import sys, signal

    RUNNING = True

    def signal_handler(signal, frame):
        global RUNNING
        RUNNING = False
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    join_all_resp = requests.get(PLAYER_API_BASE_URL + "/join_all")
    console.log("[App] - Starting")

    while RUNNING:
        lner = listener.accept()
        log_connection(*lner)

        def run():
            try:
                console.log("Handling Connection")
                handle_connection(*lner)
            except Exception as exc:
                console.log(exc)
                ...

            try:
                CONNECTIONS.pop(lner[1])
            except:
                ...

        future = executor.submit(run)
        # t = Thread(target=run)
        # t.setDaemon(True)
        # t.start()
