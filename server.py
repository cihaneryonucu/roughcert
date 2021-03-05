import zmq
import argparse
import threading
import time
import socket

import contacts_pb2 as cpb
from protobuf_to_dict import protobuf_to_dict, dict_to_protobuf


class Server(object):
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
            self.parse_command(action)
            if self._stop_event.isSet():
                break

    def monitor_loop(self):
        while True:
            print(self.userList)
            time.sleep(10)

    def unpack_user(self, action):
        return protobuf_to_dict(action.user)

    def parse_command(self, action):
        reply = cpb.server_action()
        if action.action == 'CTS':                   #request all contacts on the server currently
            reply.action = 'ACK'
            for users in self.userList:
                reply.contacts.user.add()
                user = dict_to_protobuf(cpb.User, values=users)
                reply.contacts.user.append(user)
            self.socket.send(reply.SerializeToString())
        elif action.action == 'REG':                 #Register a new contact on the server - check if already present
            new_user = self.unpack_user(action)
            if new_user not in self.userList:
                self.userList.append(new_user)
            else:
                print('User is present already! ')
            print(self.userList)
            reply.action = 'ACK'
            self.socket.send(reply.SerializeToString())
        elif action.action == 'DEL':
            del_user = self.unpack_user(action)     #Remove the contact from the server - throw exception if contact not present
            try:
                self.userList.remove(del_user)
            except ValueError:
                print("User not in list")
            reply.action = 'ACK'
            self.socket.send(reply.SerializeToString())
        elif action.action == 'ACK':
            print('Client ACk\'d our reply')
            reply.action = 'ACK'
            self.socket.send(reply.SerializeToString())
        else:
            print("Request malformed - nothing to do")

    def run(self):
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
            pass
    except KeyboardInterrupt as e:
        server.stop()
    except:
        raise