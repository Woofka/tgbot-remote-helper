import asyncio
import socket
import re
import binascii
import subprocess
from protocol import Protocol
import datetime
import time
import logging
import os

from config import LOG_ID


log = logging.getLogger('logger')

BCAST = '<broadcast>'
WAKEONLAN_PORT = 9
PROTO_PORT_SERVER = 10788
PROTO_PORT_CLIENT = 10789


STATUS_FILE_NAME = 'status.info'
STATUS_MAX_UNCHANGED = 15


sock_proto = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
sock_proto.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
sock_proto.bind(('', PROTO_PORT_CLIENT))
sock_proto.settimeout(0.001)


def _mac_bytes_to_str(_bytes, sep=':'):
    return binascii.hexlify(_bytes, sep=sep, bytes_per_sep=1).decode('ASCII')


def _parse_mac_addr(msg_args):
    result = re.findall(r'(?: |^)([0-9a-fA-F]{2}(?:[:\.-][0-9a-fA-F]{2}){5})(?: |$)', msg_args)
    if len(result) > 0:
        mac_str = re.sub(r'[:\.-]', '', result[0].lower())
        mac = binascii.unhexlify(mac_str)
        return mac
    return None


def _correct_mac(mac_addr, sep='-'):  # windows: sep='-'
    mac = _parse_mac_addr(mac_addr)
    return _mac_bytes_to_str(mac, sep=sep)


def _form_magic_packet(b_mac_addr):
    packet = b'\xff'*6 + b_mac_addr*16
    return packet


def wake_on_lan(mac_addr):
    b_mac_addr = _parse_mac_addr(mac_addr)
    packet = _form_magic_packet(b_mac_addr)
    sock_proto.sendto(packet, (BCAST, WAKEONLAN_PORT))


def ask_uptime(mac_addr, user_id, chat_id):
    ip = _get_lan_ip(mac_addr)
    if ip is not None:
        packet = Protocol(Protocol.CODE_ASKSTARTTIME, user_id, chat_id).encode()
        sock_proto.sendto(packet, (ip, PROTO_PORT_SERVER))
        return True
    else:
        return False


def _get_lan_ip(mac_addr):
    mac_addr = _correct_mac(mac_addr)
    cmd_res = subprocess.run(['arp', '-a'], stdout=subprocess.PIPE)
    # cmd_res = cmd_res.stdout.decode('UTF-8')
    cmd_res = cmd_res.stdout.decode('cp866')  # windows
    for s in cmd_res.split('\n'):
        if mac_addr in s:
            ip = re.findall(r'(\d{1,3}(?:\.\d{1,3}){3})', s)[0]
            return ip


def get_last_status():
    if os.path.exists(STATUS_FILE_NAME):
        with open(STATUS_FILE_NAME, 'r') as f:
            statuses = f.readlines()
            status = (statuses[0].replace('\n', '') == 'True')
            return status, float(statuses[1])  # last status, last response time
    else:
        return False, 0.0


def _update_status(status, timestamp):
    log.debug(f'Update status to {status} {timestamp}')
    with open(STATUS_FILE_NAME, 'w') as f:
        f.write(f'{status}\n{timestamp}')


async def protocol_handler(bot):
    await asyncio.sleep(3)  # wait for bot start
    while True:
        try:
            data, source = sock_proto.recvfrom(1024)
            packet = Protocol.decode(data)

            if packet.code == Protocol.CODE_IFALIVE:
                status_info = _handle_status(True, datetime.datetime.now().timestamp())
                if status_info:
                    await bot.send_message(LOG_ID, '[INFO] Device is running now')

            if packet.code == Protocol.CODE_STARTTIME:
                startup_time = datetime.datetime.fromisoformat(packet.payload)
                await bot.send_message(packet.cid, f'[WorkInProgress] Startup time: {startup_time}')
                # TODO handle this info in the way I want
        except socket.timeout:
            await asyncio.sleep(0.01)
        except Exception as err:
            log.error(f'[protocol_handler] {err}')
            await bot.send_message(LOG_ID, f'[ERROR:protocol_handler] {err}')


def _handle_status(status, timestamp):
    last_status, last_response = get_last_status()
    diff = timestamp - last_response
    if status:
        _update_status(status, timestamp)
        if status == last_status and diff < STATUS_MAX_UNCHANGED:  # still online
            return None
        return True  # now it's online, but was offline before

    if status != last_status and diff > STATUS_MAX_UNCHANGED:  # it probably became offline
        _update_status(status, last_response)
        return False
    return None  # still offline


async def status_observer(bot):
    await asyncio.sleep(3)  # wait for bot start
    packet = Protocol(Protocol.CODE_IFALIVE, 0, 0).encode()
    while True:
        sock_proto.sendto(packet, (BCAST, PROTO_PORT_SERVER))
        status_info = _handle_status(False, datetime.datetime.now().timestamp())
        if status_info is False:
            await bot.send_message(LOG_ID, '[INFO] Device is probably offline now')
        await asyncio.sleep(5)
