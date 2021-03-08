import unittest

from connectionManager import connection_manager

class TestNetworking(unittest.TestCase){

    def test_register_user(self):

        contactList = [{"username" : "marco", "ipAddr" : "10.0.0.1", "port" : "10000"}]
        local_user = {"username" : "marco", "ipAddr" : "10.0.0.1", "port" : "10000"}
        #setup socket for tessting

        


        connection_manager("127.0.0.1", local_user=local_user)



        pass


}

if __name__ == '__main__':
    unittest.main()