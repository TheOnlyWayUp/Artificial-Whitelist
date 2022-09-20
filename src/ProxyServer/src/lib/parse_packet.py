"""Module to store Packet Parsers."""

from typing import Dict


def parse_handshake_packet(packet: bytes) -> Dict[str, str]:
    """Parse a handshake packet and extract the username and hostname"""

    username = ""
    hostname = ""

    watching_username = False
    watching_hostname = False

    for idx, bit in enumerate(packet):
        information = {"chr": chr(bit), "raw": bit, "idx": idx}

        if information["chr"] == "*":
            watching_hostname = True
            continue
        elif information["chr"] == '"':
            watching_hostname = None
            continue

        if watching_hostname:
            hostname += information["chr"]
        elif watching_username:
            username += information["chr"]

        if watching_hostname is None:
            watching_username = True

    if not username.isalnum():
        username = "".join(ch for ch in username if ch.isalnum())

    return {"username": username, "hostname": hostname}


def check_if_packet_c2s_encryption_response(packet: bytes) -> bool:
    """Check if a packet is the Client->Server Encryption Response Packet."""
    parsed = [_ for _ in packet]
    if [133, 2, 1] != parsed[:3]:
        return False
    if [128, 1] != parsed[133:135]:
        return False
    # 2 am code (This code isn't the best of quality, but will work. If rewritten to determine if a packet is a c2s encryption response packet with 100% certainity, it would make it harder to bypass)
    return True


def check_if_packet_motd_packet(packet: bytes, server_motd: str) -> bool:
    """Check if a packet is the MOTD Response Packet.
    This is done by checking if the Server MOTD is in the packet response."""
    return server_motd in packet.decode("latin-1")
