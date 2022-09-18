def parse_handshake_packet(packet: bytes):
    # Parse a handshake packet and extract the username and hostname

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

    try:
        username.isalnum()
    except:
        username = "".join(ch for ch in username if ch.isalnum())

    return {"username": username, "hostname": hostname}


def check_if_packet_c2s_encryption_response(packet: bytes):
    parsed = [_ for _ in packet]
    if [133, 2, 1] != parsed[:3]:
        return False
    if [128, 1] != parsed[133:135]:
        return False
    # 2 am code (This code isn't the best of quality, but will work. If rewritten to determine if a packet is a c2s encryption response packet with 100% certainity, it would make it harder to bypass)
    return True


def check_if_packet_motd_packet(packet: bytes, server_motd: str):
    return server_motd in packet.decode("latin-1")
