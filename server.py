import zmq
import argparse
import threading
import time
import logging
import socket

import contacts_pb2 as cpb
from protobuf_to_dict import protobuf_to_dict, dict_to_protobuf

from LogMixin import LogMixin

class Server(LogMixin):
    def __init__(self, port=10040):

        self.port = port
        self.userList = []
        self.socket = None
        self.server_address = None
        self.poller = zmq.Poller()
        self._stop_event = threading.Event()
        self._thread = None
        self._thread_monitor = None

    def connect(self):
        #find the local IP
        self.socket =  zmq.Context().instance().socket(zmq.REP)
        connect_string = 'tcp://*:{}'.format(self.port)
        self.socket.bind(connect_string)

    def server_loop(self):
        action = cpb.server_action()
        while True:
            data = self.socket.recv()
            action.ParseFromString(data)
            reply = self.parse_command(action)
            self.socket.send(reply.SerializeToString())
            if self._stop_event.isSet():
                break

    def monitor_loop(self):
        while True:
            self.logger.info(self.userList)
            time.sleep(10)

    def unpack_user(self, action):
        return protobuf_to_dict(action.user)

    def register_user(self, action):
        reply = cpb.server_action()
        new_user = self.unpack_user(action)
        if new_user not in self.userList:
            self.userList.append(new_user)
            reply.result('Added user to contact list')
        else:
            self.logger.WARNING('User is present already! ')
            reply.result('User is already present in contact contact list')
        self.logger.info(self.userList)
        reply.action = 'ACK'
        return reply
    
    def delete_user(self, action):
        reply = cpb.server_action()
        del_user = self.unpack_user(action)     #Remove the contact from the server - throw exception if contact not present
        try:
            self.userList.remove(del_user)
            reply.result('Deleted user from contact list')
        except ValueError:
            self.logger.WARNING("User not in list")
            reply.result('User is not present in contact list')
        reply.action = 'ACK'
        return reply

    def list_all_available_users(self, action):
        reply = cpb.server_action()
        for users in self.userList:
            reply.contacts.user.add()
            user = dict_to_protobuf(cpb.User, values=users)
            reply.contacts.user.append(user)
        reply.action = 'ACK'
        reply.result('Server listing all possible user')
        return reply

    def ack_to_request(self):
        reply = cpb.server_action()
        self.logger.info('Client ACk\'d our reply')
        reply.action = 'ACK'
        return reply

    def n_ack_to_request(self):
        reply = cpb.server_action()
        self.logger.ERROR('Cannot ACK request')
        reply.action = 'NACK'
        reply.message = 'Malformed request'
        return reply

    def parse_command(self, action):
        if action.action == 'CTS':                   #request all contacts on the server currently
            reply = self.list_all_available_users(action)
        elif action.action == 'REG':                 #Register a new contact on the server - check if already present
            reply = self.register_user(action=action)
        elif action.action == 'DEL':
            reply = self.delete_user(action=action)
        elif action.action == 'ACK':
            reply = self.ack_to_request()
        else:
            reply = self.n_ack_to_request()
            self.logger.ERROR("Request malformed - nothing to do")
        return reply

    def run(self):
        self.logger.debug("Bootstrap Server")
        self.connect()
        self._thread = threading.Thread(target=self.server_loop)
        self._thread.daemon = True
        self._thread.start()
        self._thread_monitor = threading.Thread(target=self.monitor_loop)
        self._thread_monitor.daemon = True
        self._thread_monitor.start()

    def stop(self):
        self.socket.close()
        self._stop_event.set()
        self._thread.join()


def input_argument():
    parser = argparse.ArgumentParser(description='Secure Chat backend')
    parser.add_argument('--port',
                        type=int,
                        help='Backend port (def: 10000')
    return parser.parse_args()

if __name__ == '__main__':
    print('Secure Chat Backend')
    try:
        args = input_argument()
        if args.port != None:
            server = Server(port=args.port)
        else:
            server = Server()
        server.run()
        while True:
            time.sleep(10)
    except KeyboardInterrupt as e:
        server.stop()
    except:
        raise