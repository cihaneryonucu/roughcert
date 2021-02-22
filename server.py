if __name__ == '__main__':
    raise Exception("This module cannot be run as an executable!")

import zmq
import threading

import message_pb2



class Sender(object):
    def __init__(self, chat_address, chat_port, chat_pipe):
        self.chat_address = chat_address
        self.chat_port = chat_port
        self.context = zmq.Context()
        self.tx_sock = None
        self.chat_pipe = chat_pipe

    def connect(self):
        self.tx_sock = zmq.context.socket(zmq.PUB)
        connect_string = 'tcp://{}:{}'.format(
            self.chat_address, self.chat_port)
        self.tx_sock.connect(connect_string)

    def reconnect_to_server(self):
        self.tx_sock.setsockopt(zmq.LINGER, 0)
        self.tx_sock.close()
        self.connect()

    def get_new_message(self):
        return self.chat_pipe.recv_string()

    def send_message(self, message):
        self.tx_sock.send(message)

    def receive_message(self):
        self.tx_sock.recv()

    def sender_loop(self):
        self.connect()
        while True:
            message = self.get_new_message()
            self.send_message(message)

    def run(self):
        thread = threading.Thread(target=self.sender_loop())
        thread.daemon = True
        thread.start()


class Receiver(object):
    def __init__(self, chat_port, chat_pipe):
        self.chat_port = chat_port
        self.context = zmq.Context()
        self.rx_sock = None
        self.history = chat_pipe
        self.poller = zmq.Poller()

    def connect(self):
        self.rx_sock = zmq.context.socket(zmq.SUB)
        connect_string = 'tcp://*:{}'.format(self.chat_port)
        self.rx_sock.connect(connect_string)

    def push_message_to_history(self, message):
        self.history.send(message)

    def register_with_poller(self):
        self.poller.register(self.rx_sock, zmq.POLLIN)

    def has_message(self):
        events = dict(self.poller.poll(3000))
        return events.get(self.rx_sock) == zmq.POLLIN

    def get_message(self):
        return self.rx_sock.recv()

    def receiver_loop(self):
        self.connect()
        self.register_with_poller()
        while True:
            if self.has_message():
                message = self.get_message()
                self.push_message_to_history(message)

    def run(self):
        thread = threading.Thread(target=self.receiver_loop)
        thread.daemon = True
        thread.start()
