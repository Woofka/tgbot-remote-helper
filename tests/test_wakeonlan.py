import unittest

from bot_utils import parse_mac_addr, form_magic_packet


class TestParseMacAddr(unittest.TestCase):
    def test_mac_default(self):
        mac = '1a:b2:c3:0a:ff:99'
        result = parse_mac_addr(mac)
        expected = b'\x1a\xb2\xc3\x0a\xff\x99'
        self.assertEqual(expected, result)

    def test_mac_dot_sep(self):
        mac = '1a.b2.c3.0a.ff.99'
        result = parse_mac_addr(mac)
        expected = b'\x1a\xb2\xc3\x0a\xff\x99'
        self.assertEqual(expected, result)

    def test_mac_dash_sep(self):
        mac = '1a-b2-c3-0a-ff-99'
        result = parse_mac_addr(mac)
        expected = b'\x1a\xb2\xc3\x0a\xff\x99'
        self.assertEqual(expected, result)

    def test_mac_upper_case(self):
        mac = '1A:B2:C3:0A:FF:99'
        result = parse_mac_addr(mac)
        expected = b'\x1a\xb2\xc3\x0a\xff\x99'
        self.assertEqual(expected, result)

    def test_mac_extra_symbols(self):
        mac = 'My mac is 1a:b2:c3:0a:ff:99 check it please'
        result = parse_mac_addr(mac)
        expected = b'\x1a\xb2\xc3\x0a\xff\x99'
        self.assertEqual(expected, result)

    def test_mac_shorter(self):
        mac = '1a:b2:c3:0a:ff'
        result = parse_mac_addr(mac)
        expected = None
        self.assertEqual(expected, result)

    def test_mac_longer(self):
        mac = '1a:b2:c3:0a:ff:99:aa'
        result = parse_mac_addr(mac)
        expected = None
        self.assertEqual(expected, result)

    def test_mac_wrong_bytes(self):
        mac = '1a:b2:g3:0a:if:99'
        result = parse_mac_addr(mac)
        expected = None
        self.assertEqual(expected, result)


class TestFormMagicPacket(unittest.TestCase):
    def test_form_magic_packet(self):
        mac = b'\x1a\xb2\xc3\n\xff\x99'
        result = form_magic_packet(mac)
        expected = b'\xff\xff\xff\xff\xff\xff\x1a\xb2\xc3\n\xff\x99\x1a\xb2\xc3\n\xff\x99\x1a\xb2\xc3\n\xff\x99\x1a\xb2\xc3\n\xff\x99\x1a\xb2\xc3\n\xff\x99\x1a\xb2\xc3\n\xff\x99\x1a\xb2\xc3\n\xff\x99\x1a\xb2\xc3\n\xff\x99\x1a\xb2\xc3\n\xff\x99\x1a\xb2\xc3\n\xff\x99\x1a\xb2\xc3\n\xff\x99\x1a\xb2\xc3\n\xff\x99\x1a\xb2\xc3\n\xff\x99\x1a\xb2\xc3\n\xff\x99\x1a\xb2\xc3\n\xff\x99\x1a\xb2\xc3\n\xff\x99'
        self.assertEqual(expected, result)


if __name__ == '__main__':
    unittest.main()
