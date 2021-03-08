import unittest

from connectionManager import connection_manager
import server

import message_pb2 as pbc

class TestNetworking(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contactList = [{"username" : "marco", "ipAddr" : "10.0.0.1", "port" : "10000"}]
        cls.local_user = {"username" : "marco", "ipAddr" : "10.0.0.1", "port" : "10000"}
        cls.second_user = {"username": "frank", "ipAddr": "10.0.0.2", "port": "10002"}
        cls.connection_manager = None
        cls.server = server.Server(port=9998)
        cls.server.run()
        cls.connection_manager = connection_manager("127.0.0.1", local_user=cls.local_user, port=9998)
        cls.connection_manager.connect()

    def test_register_user(cls):
        print('TEST #1: Test user registration process')
        request = cls.connection_manager.register_user()
        cls.assertEqual(request.action, "ACK", "Server ack'd correctly")
        cls.assertEqual(request.result, "Added user to contact list", "Added user from contact list")

    def test_request_users(cls):
        print('TEST #2: Test user request process')
        request = cls.connection_manager.request_users()
        cls.assertEqual(request.action, "ACK", "Server ack'd correctly")
        cls.assertEqual(request.result, 'Server listing all possible user', 'Server listing all possible user')
        cls.assertEqual(cls.connection_manager.contactList, [], "Contact Lists are equal - only one person should be available")

    def test_remove_user(cls):
        print('TEST #3: Test user removal process')
        request = cls.connection_manager.remove_user()
        cls.assertEqual(request.action, "ACK", "Server ack'd correctly")
        cls.assertEqual(request.result, "Deleted user from contact list", "Deleted user from contact list")
        cls.assertEqual(cls.connection_manager.contactList, [], "Contact Lists are equal - only one person should be available")

if __name__ == '__main__':
    unittest.main()