import unittest
import zmq

import server
import contacts_pb2 as cpb
from protobuf_to_dict import protobuf_to_dict, dict_to_protobuf


class TestNetworking(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = server.Server()

    def test_server_connect(cls):
        print('TEST #1: server can connect to the specific socket')
        cls.server.connect()
        cls.assertIsNot(cls.server.socket, None, "Opened socket descriptor successfully")

    def test_unpack_user(cls):
        print("TEST #2: unpack user from protobuf to dict")
        second_user = {'username': 'frank', 'ipAddr': '10.0.0.2', 'port': 10002}
        user = cpb.User()
        user.username = second_user.get('username')
        user.ipAddr = second_user.get('ipAddr')
        user.port = int(second_user.get('port'))
        cls.assertEqual(protobuf_to_dict(user), second_user, 'Users Match')

    def test_nacking(cls):
        print("TEST #3: nack from server")
        request = cpb.server_action()
        request.action = 'WUT'
        resp = cls.server.parse_command(request)
        cls.assertEqual(resp.action, 'NACK', 'Server Nack is correct')

    def test_acking(cls):
        print("TEST #4: ack from server")
        request = cpb.server_action()
        request.action = 'ACK'
        resp = cls.server.parse_command(request)
        cls.assertEqual(resp.action, 'ACK', 'Server Nack is correct')

    def test_add_user(cls):
        print('TEST #5: add user to server')
        second_user = {'username': 'frank', 'ipAddr': '10.0.0.2', 'port': 10002}
        userList = []
        userList.append(second_user)
        request = cpb.server_action()
        request.action = 'REG'
        request.user.username = second_user.get('username')
        request.user.ipAddr = second_user.get('ipAddr')
        request.user.port = int(second_user.get('port'))
        resp = cls.server.parse_command(request)
        cls.assertEqual(cls.server.userList, userList, 'Server Appends one user')
        cls.assertEqual(resp.result, 'Added user to contact list', 'Added user to contact list')
        resp = cls.server.parse_command(request)
        cls.assertEqual(cls.server.userList, userList, 'Server does not append the same user again')
        cls.assertEqual(resp.result, 'User is already present in contact contact list', 'User is already present in contact contact list')

    def test_remove_user(cls):
        print('TEST #6: remove user to server')
        second_user = {'username': 'frank', 'ipAddr': '10.0.0.2', 'port': 10002}
        request = cpb.server_action()
        request.action = 'DEL'
        request.user.username = second_user.get('username')
        request.user.ipAddr = second_user.get('ipAddr')
        request.user.port = int(second_user.get('port'))
        resp = cls.server.parse_command(request)
        cls.assertEqual(cls.server.userList, [], 'Server remove one user')
        cls.assertEqual(resp.result, 'Deleted user from contact list')
        resp = cls.server.parse_command(request)
        cls.assertEqual(cls.server.userList, [], 'Server does not attempt remove non existing users')
        cls.assertEqual(resp.result, 'User is not present in contact list', 'Cannot remove non existing users')


if __name__ == '__main__':
    unittest.main()