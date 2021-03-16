if __name__ == '__main__':
    raise Exception("This module cannot be run as an executable!")

import threading
from Crypto import *
from LogMixin import LogMixin


class User(object, LogMixin):
    def __init__(self, control_port=9999, local_user=None):
        self.control_port = control_port
        self.control_socket = None
        self.control_remote = None
        self.crypto = None
        self.localUser = local_user
        self.handshake_is_done = 0
        self.remote_address = None
        self.isInitiator = False
        self.remote_peer_address = None

    def set_remote_address(self, address):
        self.remote_peer_address = address

    def set_initiator(self):
        self.isInitiator = True

    def handshake(self):
        while not self.isInitiator:
            self.control_socket = zmq.Context().instance().socket(zmq.PAIR)
            self.control_socket.bind('tcp://*:{}'.format(self.control_port))
            message = self.control_socket.recv_string()
            if message == 'HSK':
                self.crypto = Crypto_Primitives(self.control_socket,
                                            import_private_key('./credentials/{}_private_key.pem'.format(self.localUser.get('keyBase'))),
                                            import_certificate('./credentials/{}_cert.pem'.format(self.localUser.get('keyBase'))),
                                            import_certificate('./credentials/CA_cert.pem'))
                self.crypto.establish_session_key(False)
                self.control_socket.send_string('ACK')
            elif message == 'ACK': # for the initiator to kill this thread
                pass
            self.isInitiator = True

    def force_request(self):
        self.control_remote = zmq.Context().instance().socket(zmq.PAIR)
        self.control_remote.connect('tcp://{}:{}'.format(self.remote_peer_address, self.control_port))
        self.control_remote.send_string('HSK')
        self.crypto = Crypto_Primitives(self.control_remote,
                                        import_private_key('./credentials/{}_private_key.pem'.format(self.localUser.get('keyBase'))),
                                        import_certificate('./credentials/{}_cert.pem'.format(self.localUser.get('keyBase'))),
                                        import_certificate('./credentials/CA_cert.pem'))
        self.crypto.establish_session_key(True)

    def run(self):
        thread = threading.Thread(target=self.handshake)
        thread.daemon = True
        thread.start()


class Sender(object, LogMixin):
    def __init__(self, crypto, remote_peer, outbox):
        self.remote_peer = remote_peer
        self.tx_sock = None
        self.outbox_queue = outbox
        self.crypto = crypto

    def connect(self):
        self.tx_sock = zmq.Context().instance().socket(zmq.PAIR)
        self.tx_sock.connect('tcp://{}:{}'.format(self.remote_peer.get('ipAddr'), self.remote_peer.get('port')))

    def receive_message(self):
        self.tx_sock.recv()

    def sender_loop(self):
        while True:
            message = self.crypto.encrypt(self.outbox_queue.get())
            self.tx_sock.send(message, flags=zmq.NOBLOCK)

    def get_outbox_queue(self):
        return self.outbox_queue

    def run(self):
        self.connect()
        thread = threading.Thread(target=self.sender_loop())
        thread.daemon = True
        thread.start()


class Receiver(object, LogMixin):
    def __init__(self, crypto, local_user, inbox):
        self.local_user = local_user
        self.rx_sock = None
        self.inbox_queue = inbox
        self.crypto = crypto

    def connect(self):
        self.rx_sock = zmq.Context().instance().socket(zmq.PAIR)
        self.rx_sock.bind('tcp://{}:{}'.format(self.local_user.get('ipAddr'), self.local_user.get('port')))

    def receiver_loop(self):
        while True:
            message = self.crypto.decrypt(self.rx_sock.recv())
            self.inbox_queue.put(message)

    def get_inbox_queue(self):
        return self.inbox_queue

    def run(self):
        self.connect()
        thread = threading.Thread(target=self.receiver_loop)
        thread.daemon = True
        thread.start()
