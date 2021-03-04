
import curses
import argparse
import sys
import time
import datetime
import zmq
from requests import get

from inquirer import Checkbox, prompt
from protobuf_to_dict import protobuf_to_dict

from queue import SimpleQueue
import threading

from curses import wrapper

import message_pb2 as pbm
import chat

import contacts_pb2 as pbc

def certificate_window(window, log):
    window_lines, window_cols = window.getmaxyx()
    window.bkgd(curses.A_NORMAL, curses.color_pair(2))
    window.box()
    title = " Peer certificate "
    window.addstr(0, int((window_cols  - len(title)) / 2 + 1), title)
    window.refresh()

    #Validate Certificate here

def logbook_window(window, log):
    window_lines, window_cols = window.getmaxyx()
    bottom_line = window_lines - 1
    window.bkgd(curses.A_NORMAL, curses.color_pair(2))
    window.scrollok(1)
    #window.box()
    title = " Logbook "
    window.addstr(0, int((window_cols - len(title)) / 2 + 1), title)
    window.refresh()
    while (True and log is not None):
        window.addstr(bottom_line, 1, log.recv_string())
        #window.move(bottom_line, 1)
        window.scroll(1)
        window.refresh()

def chat_window(window, display, log, inbox):
    window_lines, window_cols = window.getmaxyx()
    bottom_line = window_lines - 2
    window.bkgd(curses.A_NORMAL, curses.color_pair(2))
    window.scrollok(1)
    #window.box()
    title = " History "
    window.addstr(0, int((window_cols - len(title)) / 2 + 1), title)
    window.refresh()
    while True:
        # while inbox.qsize > 0: #check if we have any incoming message
        #     window.addstr(bottom_line, 1, inbox.get())
        #     window.scroll(1)
        window.refresh()
        window.addstr(bottom_line, 1, display.recv_string())
        log.send_string('[{}] RX - new message'.format(datetime.datetime.today().ctime()))
        window.scroll(1)
        window.refresh()


def input_window(window, chat_sender, log, outbox):
    window_lines, window_cols = window.getmaxyx()
    window.bkgd(curses.A_NORMAL, curses.color_pair(2))
    window.clear()
    window.box()
    title = " Input "
    window.addstr(0, 0, title)
    window.refresh()
    curses.curs_set(1)
    while True:
        window.clear()
        window.box()
        window.refresh()
        s = window.getstr(1, 1).decode('utf-8')
        if s is not None and s != "":
            chat_sender.send_string(s)
            outbox.put(s)
            log.send_string('[{}] TX - new message'.format(datetime.datetime.today().ctime()))
        time.sleep(0.5)

def input_argument():
    parser = argparse.ArgumentParser(description='Secure Chat client with message self destruct')
    parser.add_argument('--username',
                        type=str,
                        help='Username of sender')
    parser.add_argument('--port',
                        type=str,
                        help='port of sender')
    return parser.parse_args()


def main_app(stdscr, remotePeer, localUser):

    ### curses set up

    #Clear screen
    stdscr.clear()

    sock_history = zmq.Context().instance().socket(zmq.PAIR)
    sock_history.bind("inproc://history")

    sock_log = zmq.Context().instance().socket(zmq.PAIR)
    sock_log.bind("inproc://log")

    logging = zmq.Context().instance().socket(zmq.PAIR)
    logging.connect("inproc://log")

    sock_input = zmq.Context().instance().socket(zmq.PAIR)
    sock_input.connect("inproc://history")

    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLACK)
    #User echo to screen
    curses.echo()
    curses.curs_set(0)

    window_w = curses.COLS
    window_h = curses.LINES
    #print(window_w, window_h)
    h_splitter = int(window_h * 0.9)
    v_splitter = int(window_w * 0.65)
    h_l_splitter = int(window_h * 0.5)

    chat_pad = stdscr.subpad(h_splitter, v_splitter, 0, 0)
    input_pad = stdscr.subpad(window_h - h_splitter, v_splitter, h_splitter, 0)
    certificate_pad = stdscr.subpad(h_l_splitter, window_w - v_splitter, 0, v_splitter)
    logbook_pad = stdscr.subpad(window_h - h_l_splitter, window_w - v_splitter, h_l_splitter, v_splitter)


    #None arguments are for testing

    inbox = SimpleQueue()
    outbox = SimpleQueue()

    chat_history = threading.Thread(target=chat_window, args=(chat_pad, sock_history, logging, inbox))
    chat_history.daemon = True
    chat_history.start()
    time.sleep(0.05)

    cert_view = threading.Thread(target=certificate_window, args=(certificate_pad, logging))
    cert_view.daemon = True
    cert_view.start()
    time.sleep(0.05)

    chat_sender = threading.Thread(target=input_window, args=(input_pad, sock_input, logging, outbox))
    chat_sender.daemon = True
    chat_sender.start()
    time.sleep(0.05)

    logbook = threading.Thread(target=logbook_window, args=(logbook_pad, sock_log))
    logbook.daemon = True
    logbook.start()
    time.sleep(0.05)

    chat_tx = chat.Sender(chat_address=remotePeer.get('ipAddr'), chat_port=remotePeer.get('port'), outbox=outbox)
    chat_rx = chat.Receiver(chat_port=localUser.get('port'), inbox=inbox)

    chat_tx.run()
    chat_rx.run()


    chat_history.join()
    cert_view.join()
    chat_sender.join()
    logbook.join()

class connection_manager(object):
    def __init__(self, server, local_user=None, port=10000):
        self.server = server
        self.port = port
        self.sock_backend = None
        self.contactList = []
        self.local_user = local_user

    def connect(self):
        self.sock_backend = zmq.Context().instance().socket(zmq.REQ)
        self.sock_backend.connect('tcp://{}:10000'.format(self.server))

    def register_user(self):
        request = pbc.server_action()
        request.action = 'REG'
        request.user.username = args.username
        request.user.ipAddr = '{}'.format(get('https://api.ipify.org').text)
        request.user.port = int(args.port)
        request.user.isUp = 'OK'
        request.requestTime = int(time.time())
        self.sock_backend.send(request.SerializeToString())
        print('Sent REG')
        data = self.sock_backend.recv()
        resp = pbc.server_action()
        resp.ParseFromString(data)
        if resp.action == 'ACK':
            print('Success')
            self.local_user = protobuf_to_dict(request.user)


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
        print('Sent CTS')
        data = self.sock_backend.recv()
        resp = pbc.server_action()
        resp.ParseFromString(data)
        if resp.action == 'ACK':
            print('Success')
            self.contactList = self._unpack_user_list(resp)

    def getContactList(self):
        return self.contactList

    def getLocalUser(self):
        return self.local_user


if __name__ == "__main__":
    print(" ---- Secure Chat ----")
    try:
        # check input arguments
        args = input_argument()
        if args.username is None:
            sys.exit('Error - specify an username')

        print("Bootstrap: create contact entry for this user")
        connection_manager = connection_manager(server='127.0.0.1')
        connection_manager.connect()
        connection_manager.register_user()
        check_for_peers = [
            Checkbox('Check for peers',
                     message='Do you want to check for peers?',
                     choices=['yes', 'no'])
        ]

        connection_manager.request_users()
        contactList = connection_manager.getContactList()

        while not contactList:
            answer = prompt(check_for_peers)
            print(answer.get('Check for peers'))
            if answer.get('Check for peers') == ['yes']:
                connection_manager.request_users()
                contactList = connection_manager.getContactList()
            else:
                break

        if not contactList:
            print("I mean... you gotta be talking to someboby right? bye...")
            sys.exit(0)

        questions = [
            Checkbox('Peers',
                     message='Select a peer to connect to',
                     choices=contactList)
            ]
        answer = prompt(questions)
        print(answer)
        peer = answer.get('Peers')[0]
        print(peer.get('ipAddr'), peer.get('port'))
        input()
        wrapper(main_app, peer, connection_manager.getLocalUser())
    except KeyboardInterrupt as e:
        pass
    except:
        raise
