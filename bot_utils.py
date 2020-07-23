import socket
import re
import binascii


BCAST = '<broadcast>'
WAKEONLAN_PORT = 9


def mac_bytes_to_str(_bytes):
    return binascii.hexlify(_bytes, sep=':', bytes_per_sep=1).decode('ASCII')


def parse_mac_addr(msg_args):
    result = re.findall(r'(?: |^)([0-9a-fA-F]{2}(?:[:\.-][0-9a-fA-F]{2}){5})(?: |$)', msg_args)
    if len(result) > 0:
        mac_str = re.sub(r'[:\.-]', '', result[0].lower())
        mac = binascii.unhexlify(mac_str)
        return mac
    return None


def form_magic_packet(mac_addr):
    packet = b'' + b'\xff'*6 + mac_addr*16
    return packet


def wake_on_lan(mac_addr):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    packet = form_magic_packet(mac_addr)

    sock.sendto(packet, (BCAST, WAKEONLAN_PORT))
