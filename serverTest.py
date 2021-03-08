import unittest

import server
import contacts_pb2 as cpb
from protobuf_to_dict import protobuf_to_dict, dict_to_protobuf


class TestNetworking(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = server.Server()

    def server_connect(cls):
        print('TEST #1: server can connect to the specific socket')
        cls.server.connect()
        cls.assertIsNone(cls.server.socket, "Opened socket descriptor successfully")

    def test_unpack_user(cls):
        print("TEST #2: unpack user from protobuf to dict")
        second_user = {'username': 'frank', 'ipAddr': '10.0.0.2', 'port': 10002}
        user = cpb.User()
        user.username = second_user.get('username')
        user.ipAddr = second_user.get('ipAddr')
        user.port = int(second_user.get('port'))
        cls.assertEqual(protobuf_to_dict(user), second_user, 'Users Match')



if __name__ == '__main__':
    unittest.main()