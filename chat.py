if __name__ == '__main__':
    raise Exception("This module cannot be run as an executable!")

import zmq
import threading

import message_pb2
from queue import SimpleQueue


class Sender(object):
    def __init__(self, chat_address, chat_port, outbox):
        self.chat_address = chat_address
        self.chat_port = chat_port
        self.context = zmq.Context()
        self.tx_sock = None
        self.chat_pipe = outbox
        print(self.chat_address, self.chat_port)

    def connect(self):
        self.tx_sock = zmq.Context().instance().socket(zmq.PAIR)
        self.tx_sock.connect('tcp://{}:{}'.format(self.chat_address, self.chat_port))

    def reconnect_to_server(self):
        self.tx_sock.setsockopt(zmq.LINGER, 0)
        self.tx_sock.close()
        self.connect()

    def get_new_message(self):
        return self.chat_pipe.get()

    def send_message(self, message):
        self.tx_sock.send_string(message)

    def receive_message(self):
        self.tx_sock.recv()

    def sender_loop(self):
        while True:
            message = self.get_new_message()
            self.send_message(message)

    def outboxQueue(self):
        return self.outboxQueue

    def run(self):
        self.connect()
        thread = threading.Thread(target=self.sender_loop())
        thread.daemon = True
        thread.start()


class Receiver(object):
    def __init__(self,chat_address, chat_port, inbox):
        self.chat_address = chat_address
        self.chat_port = chat_port
        self.context = zmq.Context()
        self.rx_sock = None
        self.history = inbox
        self.poller = zmq.Poller()

    def connect(self):
        self.rx_sock = zmq.Context().instance().socket(zmq.PAIR)
        self.rx_sock.bind('tcp://{}:{}'.format(self.chat_address, self.chat_port))


    def receiver_loop(self):
        while True:
                message = self.rx_sock.recv_string()
                self.history.put(message)

    def inboxQueue(self):
        return self.inboxQueue

    def run(self):
        self.connect()
        thread = threading.Thread(target=self.receiver_loop)
        thread.daemon = True
        thread.start()
