class Protocol:
    """
    UDP packet structure:
    | code | id | payload |

    code        - packet code (1 byte). It defines type of packet
    id          - user id (4 bytes)
    payload     - payload of packet
    """
    CODE_IFALIVE = 1
    CODE_ASKSTARTTIME = 2
    CODE_STARTTIME = 3
    MUST_HAVE_PAYLOAD = (CODE_STARTTIME,)

    def __init__(self, code, uid, payload=None):
        self.code = code
        self.uid = uid
        self.payload = payload

    def __str__(self):
        return f'{self.code} {self.uid} {self.payload}'

    def encode(self):
        packet = self.code.to_bytes(1, 'big')
        packet += self.uid.to_bytes(4, 'big')
        if self.payload:
            packet += self.payload.encode('ASCII')
        return packet

    @staticmethod
    def decode(packet):
        if len(packet) < 5:
            raise Exception(f"Packet length is less than 5 bytes. Packet: {packet}")

        code = packet[0]
        uid = int.from_bytes(packet[1:5], 'big')
        payload = None
        if len(packet) > 5:
            payload = packet[5:].decode('ASCII')

        if code in Protocol.MUST_HAVE_PAYLOAD and payload is None:
            raise Exception(f"Packet must have an payload. Packet: {packet}")

        return Protocol(code, uid, payload)
