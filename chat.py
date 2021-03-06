if __name__ == '__main__':
    raise Exception("This module cannot be run as an executable!")

import zmq
import threading

import message_pb2
from queue import SimpleQueue


class Sender(object):
    def __init__(self, remote_peer_address, remote_peer_port, outbox):
        self.remote_peer_address = remote_peer_address
        self.remote_peer_port = remote_peer_port
        self.tx_sock = None
        self.outbox = outbox
        print(self.remote_peer_address, self.remote_peer_port)

    def connect(self):
        self.tx_sock = zmq.Context().instance().socket(zmq.PAIR)
        self.tx_sock.connect('tcp://{}:{}'.format(self.remote_peer_address, self.remote_peer_port))
        

    def receive_message(self):
        self.tx_sock.recv()

    def sender_loop(self):
        while True:
            message = self.outbox.get()
            self.tx_sock.send(message, flags=zmq.NOBLOCK)

    def outboxQueue(self):
        return self.outboxQueue

    def run(self):
        self.connect()
        thread = threading.Thread(target=self.sender_loop())
        thread.daemon = True
        thread.start()


class Receiver(object):
    def __init__(self, local_chat_address, local_chat_port, inbox):
        self.local_chat_address = local_chat_address
        self.local_chat_port = local_chat_port
        self.rx_sock = None
        self.inbox = inbox

    def connect(self):
        self.rx_sock = zmq.Context().instance().socket(zmq.PAIR)
        self.rx_sock.bind('tcp://{}:{}'.format(self.local_chat_address, self.local_chat_port))


    def receiver_loop(self):
        while True:
            message = self.rx_sock.recv()
            self.inbox.put(message)

    def inboxQueue(self):
        return self.inboxQueue

    def run(self):
        self.connect()
        thread = threading.Thread(target=self.receiver_loop)
        thread.daemon = True
        thread.start()
