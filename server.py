import zmq
import sys

import contacts_pb2 as cpb

class Server(object):
    def __init__(self, port):
        self.port = port
        self.userList = []
        self.socket = None
        self.poller = zmq.Poller()

    def connect(self):
        context = zmq.Context()
        self.socket = context.socket(zmq.REP)
        connect_string = 'tcp://*:{}'.format(self.port)
        self.socket.bind(connect_string)
        self.poller.register(self.socket, zmq.Poller.POLLIN)

    def receive_command(self):
        action = cpb.server_action()
        while True:
            socks = dict(self.poller.poll())
            if self.socket in socks and socks[self.socket] == zmq.POLLIN:
                action.ParseFromString(self.socket.recv())
                self.parse_command(action)

    def parse_command(self, action):
        if action.action == 'CTS':
            pass #request all contacts on the server currently
        if action.action == 'REG':
            #Register a new contact on the server - check if already present
            if action.contact.user not in self.userList:
                self.userList.append(action.contact.user)
            else:
                pass
        if action.action == 'DEL':
            #Remove the contact from the server - throw exception if contact not present
            try:
                self.userList.remove(action.contact.user)
            except ValueError:
                print("User not in list")
