import zmq
import sys
import argparse
import threading

import contacts_pb2 as cpb

class Server(object):
    def __init__(self, port=10000):
        self.port = port
        self.userList = []
        self.socket = None
        self.poller = zmq.Poller()
        self._stop_event = threading.Event()
        self._thread = None

    def connect(self):
        self.socket =  zmq.Context().instance().socket(zmq.PAIR)
        connect_string = 'tcp://127.0.0.1:{}'.format(self.port)
        self.socket.bind(connect_string)

    def server_loop(self):
        action = cpb.server_action()
        while True:
            data = self.socket.recv()
            action.ParseFromString(data)
            self.parse_command(action)
            if self._stop_event.isSet():
                break

    def run(self):
        self.connect()
        self._thread = threading.Thread(target=self.server_loop)
        self._thread.start()

    def unpack_user(self, action):
        personal_data = cpb.Contacts().user.add()
        personal_data.username = action.contact.user[0].username
        personal_data.hostname = action.contact.user[0].hostname
        personal_data.isUp = action.contact.user[0].isUp
        personal_data.connectionStart = action.contact.user[0].connectionStart
        personal_data.ipAddr = action.contact.user[0].ipAddr
        personal_data.port = action.contact.user[0].port
        return personal_data

    def parse_command(self, action):
        reply = cpb.server_action()
        if action.action == 'CTS':                   #request all contacts on the server currently
            reply.action = 'ACK'
            for users in self.userList:
                reply.contact.user.add()
                reply.contact.user.append(users)
            self.socket.send(reply.SerializeToString())
        elif action.action == 'REG':                 #Register a new contact on the server - check if already present
            new_user = self.unpack_user(action)
            if new_user not in self.userList:
                self.userList.append(new_user)
            else:
                pass
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
    except KeyboardInterrupt as e:
        server.stop()
    except:
        raise