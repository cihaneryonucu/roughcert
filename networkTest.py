import unittest

from connectionManager import connection_manager


class TestNetworking(unittest.TestCase):
    def __init__(self):
        super().__init__()
        self.contactList = [{"username" : "marco", "ipAddr" : "10.0.0.1", "port" : "10000"}]
        self.local_user = {"username" : "marco", "ipAddr" : "10.0.0.1", "port" : "10000"}
        self. connection_manager = None

    def setup_testing_system(self):
        self.connection_manager = connection_manager("127.0.0.1", local_user=self.local_user)

    def test_register_user(self):
        self.assertEqual(self.connection_manager.register_user(), "ACK", "Server ack'd correctly")

    def test_request_users(self):
        self.assertEqual(self.connection_manager.request_users(), "ACK", "Server ack'd correctly")
        self.assertEqual(self.connection_manager.contactList, self.contactList, "Contact Lists are equal - only one person should be avaialble")

    def test_remove_user(self):
        self.assertEqual(self.connection_manager.remove_user(), "ACK", "Server ack'd correctly")

if __name__ == '__main__':
    unittest.main()