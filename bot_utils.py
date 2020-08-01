import socket
import re
import binascii
import subprocess
from protocol import Protocol
import datetime
import time

from config import ERROR_ID

BCAST = '<broadcast>'
WAKEONLAN_PORT = 9
PROTO_PORT_SERVER = 10788
PROTO_PORT_CLIENT = 10789

OBSERVED_STATUS = []

sock_proto = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
sock_proto.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
sock_proto.bind(('', PROTO_PORT_CLIENT))


def mac_bytes_to_str(_bytes, sep=':'):
    return binascii.hexlify(_bytes, sep=sep, bytes_per_sep=1).decode('ASCII')


def parse_mac_addr(msg_args):
    result = re.findall(r'(?: |^)([0-9a-fA-F]{2}(?:[:\.-][0-9a-fA-F]{2}){5})(?: |$)', msg_args)
    if len(result) > 0:
        mac_str = re.sub(r'[:\.-]', '', result[0].lower())
        mac = binascii.unhexlify(mac_str)
        return mac
    return None


def correct_mac(mac_addr, sep=':'):  # windows: sep='-'
    mac = parse_mac_addr(mac_addr)
    return mac_bytes_to_str(mac, sep=sep)


def _form_magic_packet(b_mac_addr):
    packet = b'\xff'*6 + b_mac_addr*16
    return packet


def wake_on_lan(mac_addr):
    b_mac_addr = parse_mac_addr(mac_addr)
    packet = _form_magic_packet(b_mac_addr)
    sock_proto.sendto(packet, (BCAST, WAKEONLAN_PORT))


def ask_status(mac_addr, user_id, chat_id):
    ip = _get_lan_ip(mac_addr)
    if ip is not None:
        packet = Protocol(Protocol.CODE_IFALIVE, user_id, chat_id).encode()
        sock_proto.sendto(packet, (ip, PROTO_PORT_SERVER))
        return True
    else:
        return False


def ask_uptime(mac_addr, user_id, chat_id):
    ip = _get_lan_ip(mac_addr)
    if ip is not None:
        packet = Protocol(Protocol.CODE_ASKSTARTTIME, user_id, chat_id).encode()
        sock_proto.sendto(packet, (ip, PROTO_PORT_SERVER))
        return True
    else:
        return False


def _get_lan_ip(mac_addr):
    mac_addr = correct_mac(mac_addr)
    cmd_res = subprocess.run(['arp', '-a'], stdout=subprocess.PIPE)
    cmd_res = cmd_res.stdout.decode('UTF-8')
    # cmd_res = cmd_res.stdout.decode('cp866')  # windows
    for s in cmd_res.split('\n'):
        if mac_addr in s:
            ip = re.findall(r'(\d{1,3}(?:\.\d{1,3}){3})', s)[0]
            return ip


def protocol_handler(bot):
    time.sleep(3)
    while True:
        try:
            data, source = sock_proto.recvfrom(1024)
            packet = Protocol.decode(data)

            print(f'[Got message from {source[0]}] {packet}')

            if packet.code == Protocol.CODE_IFALIVE:
                if packet.uid == 0:
                    pass  # TODO remember that it is alive
                else:
                    bot.send_message(packet.cid, 'Device is running')
                    # TODO send message about status

            if packet.code == Protocol.CODE_STARTTIME:
                startup_time = datetime.datetime.fromisoformat(packet.payload)
                bot.send_message(packet.cid, f'[WorkInProgress] Startup time: {startup_time}')
                # TODO handle this info in the way I want

        except Exception as err:
            bot.send_message(ERROR_ID, f'protocol_handler ERROR - {err}')


def handle_status():
    # TODO: idk, somehow I have to handle it
    pass


def status_observer():
    packet = Protocol(Protocol.CODE_IFALIVE, 0, 0).encode()
    while True:
        sock_proto.sendto(packet, (BCAST, PROTO_PORT_SERVER))
        time.sleep(5)
