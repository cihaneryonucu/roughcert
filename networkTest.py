import unittest

from connectionManager import connection_manager
import server

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
        cls.assertEqual(cls.connection_manager.register_user(), "ACK", "Server ack'd correctly")

    def test_request_users(cls):
        print('TEST #2: Test user request process')
        cls.assertEqual(cls.connection_manager.request_users(), "ACK", "Server ack'd correctly")
        cls.assertEqual(cls.connection_manager.contactList, [], "Contact Lists are equal - only one person should be available")

    def test_remove_user(cls):
        print('TEST #2: Test user removal process')
        cls.assertEqual(cls.connection_manager.remove_user(), "ACK", "Server ack'd correctly")
        cls.assertEqual(cls.connection_manager.contactList, [], "Contact Lists are equal - only one person should be available")


if __name__ == '__main__':
    unittest.main()