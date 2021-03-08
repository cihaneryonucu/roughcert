import unittest

import server

import message_pb2 as pbc

class TestNetworking(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = server.Server()
        cls.server.run()


    def server_connect(cls):
        print('TEST #1: server can connet to the specific socker')



if __name__ == '__main__':
    unittest.main()