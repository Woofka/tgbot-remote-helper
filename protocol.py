class Protocol:
    """
    UDP packet structure:
    | code | user_id | chat_id | payload |

    code        - packet code (1 byte). It defines type of packet
    user_id     - Telegram user id (4 bytes)
    chat_id     - Telegram chat id (4 bytes)
    payload     - payload of packet
    """
    CODE_IFALIVE = 1
    CODE_ASKSTARTTIME = 2
    CODE_STARTTIME = 3

    MUST_HAVE_PAYLOAD = (CODE_STARTTIME,)

    PACKET_MIN_LEN = 9
    PACKET_FIELDS_INFO = {
        'code': {'index': 0, 'length': 1},
        'uid': {'index': 1, 'length': 4},
        'cid': {'index': 5, 'length': 4},
        'payload': {'index': 9, 'length': None}
    }

    def __init__(self, code, uid, cid, payload=None):
        self.code = code
        self.uid = uid
        self.cid = cid
        self.payload = payload

    def __str__(self):
        return f'({self.code}, {self.uid}, {self.cid}, {self.payload})'

    def encode(self):
        packet = self.code.to_bytes(self.PACKET_FIELDS_INFO['code']['length'], 'big')
        packet += self.uid.to_bytes(self.PACKET_FIELDS_INFO['uid']['length'], 'big')
        packet += self.cid.to_bytes(self.PACKET_FIELDS_INFO['cid']['length'], 'big')
        if self.payload:
            packet += self.payload.encode('ASCII')
        return packet

    @staticmethod
    def decode(packet):
        if len(packet) < Protocol.PACKET_MIN_LEN:
            raise Exception(f"Packet length is less than {Protocol.PACKET_MIN_LEN}. Packet: {packet}")

        code = packet[Protocol.PACKET_FIELDS_INFO['code']['index']]

        uid_s = Protocol.PACKET_FIELDS_INFO['uid']['index']
        uid_e = uid_s + Protocol.PACKET_FIELDS_INFO['uid']['length']
        uid = int.from_bytes(packet[uid_s:uid_e], 'big')

        cid_s = Protocol.PACKET_FIELDS_INFO['cid']['index']
        cid_e = cid_s + Protocol.PACKET_FIELDS_INFO['cid']['length']
        cid = int.from_bytes(packet[cid_s:cid_e], 'big')

        payload = None
        if len(packet) > Protocol.PACKET_MIN_LEN:
            payload = packet[Protocol.PACKET_FIELDS_INFO['payload']['index']:].decode('ASCII')

        if code in Protocol.MUST_HAVE_PAYLOAD and payload is None:
            raise Exception(f"Packet must have an payload. Packet: {packet}")

        return Protocol(code, uid, cid, payload)
