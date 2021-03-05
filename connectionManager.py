import zmq
from protobuf_to_dict import protobuf_to_dict
import contacts_pb2 as pbc

import time

from LogMixin import LogMixin


class connection_manager(LogMixin):
    def __init__(self, server, local_user=None, port=10040):
        self.server = server
        self.port = port
        self.sock_backend = None
        self.contactList = []
        self.local_user = local_user

    def connect(self):
        self.sock_backend = zmq.Context().instance().socket(zmq.REQ)
        self.sock_backend.connect('tcp://{}:{}'.format(self.server, self.port))

    def register_user(self):
        request = pbc.server_action()
        request.action = 'REG'
        request.user.username = self.local_user.get('username')
        request.user.ipAddr = self.local_user.get('ipAddr')
        request.user.port = int(self.local_user.get('port'))
        request.requestTime = int(time.time())
        self.sock_backend.send(request.SerializeToString())
        self.logger.info('Sent REG')
        data = self.sock_backend.recv()
        resp = pbc.server_action()
        resp.ParseFromString(data)
        if resp.action == 'ACK':
            self.logger.info('Success')
            self.local_user = protobuf_to_dict(request.user)

    def remove_user(self):
        request = pbc.server_action()
        request.action = 'DEL'
        request.user.username = self.local_user.get('username')
        request.user.ipAddr = self.local_user.get('ipAddr')
        request.user.port = int(self.local_user.get('port'))
        request.requestTime = int(time.time())
        self.sock_backend.send(request.SerializeToString())
        self.logger.info('Sent DEL')
        data = self.sock_backend.recv()
        resp = pbc.server_action()
        resp.ParseFromString(data)
        if resp.action == 'ACK':
            self.logger.info('Success')


    def _unpack_user_list(self, action):
        userList = []
        for user in action.contacts.user:
            user_data = protobuf_to_dict(user)
            if user_data != {} and user_data != self.local_user:
                userList.append(user_data)
        return userList

    def request_users(self):
        request = pbc.server_action()
        request.action = 'CTS'
        self.sock_backend.send(request.SerializeToString())
        self.logger.info('Sent CTS')
        data = self.sock_backend.recv()
        resp = pbc.server_action()
        resp.ParseFromString(data)
        if resp.action == 'ACK':
            self.logger.info('Success')
            self.contactList = self._unpack_user_list(resp)

    def getContactList(self):
        return self.contactList

    def getLocalUser(self):
        return self.local_user

