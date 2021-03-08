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

        
if __name__ == '__main__':
    unittest.main()