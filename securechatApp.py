
import curses
import argparse
import sys
import time
import datetime
import zmq
from requests import get

from tabulate import tabulate



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

def chat_window(window, display, log):
    window_lines, window_cols = window.getmaxyx()
    bottom_line = window_lines - 2
    window.bkgd(curses.A_NORMAL, curses.color_pair(2))
    window.scrollok(1)
    #window.box()
    title = " History "
    window.addstr(0, int((window_cols - len(title)) / 2 + 1), title)
    window.refresh()
    while True:
        window.addstr(bottom_line, 1, display.recv_string())
        log.send_string('[{}] RX - new message'.format(datetime.datetime.today().ctime()))
        window.scroll(1)
        window.refresh()

def input_window(window, chat_sender, log):
    window_lines, window_cols = window.getmaxyx()
    window.bkgd(curses.A_NORMAL, curses.color_pair(2))
    window.clear()
    window.box()
    title = " Input "
    window.addstr(0, 0, title)
    window.refresh()
    while True:
        window.clear()
        window.box()
        window.refresh()
        s = window.getstr(1, 1).decode('utf-8')
        if s is not None and s != "":
            chat_sender.send_string(s)
            log.send_string('[{}] TX - new message'.format(datetime.datetime.today().ctime()))
        time.sleep(0.5)

def input_argument():
    parser = argparse.ArgumentParser(description='Secure Chat client with message self destruct')
    parser.add_argument('--username',
                        type=str,
                        help='Username of sender')
    return parser.parse_args()


def main_app(stdscr):


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

    chat_history = threading.Thread(target=chat_window, args=(chat_pad, sock_history, logging))
    chat_history.daemon = True
    chat_history.start()
    time.sleep(0.05)

    cert_view = threading.Thread(target=certificate_window, args=(certificate_pad, logging))
    cert_view.daemon = True
    cert_view.start()
    time.sleep(0.05)

    chat_sender = threading.Thread(target=input_window, args=(input_pad, sock_input, logging))
    chat_sender.daemon = True
    chat_sender.start()
    time.sleep(0.05)

    logbook = threading.Thread(target=logbook_window, args=(logbook_pad, sock_log))
    logbook.daemon = True
    logbook.start()
    time.sleep(0.05)

    chat_history.join()
    cert_view.join()
    chat_sender.join()
    logbook.join()

class connection_manager(object):
    def __init__(self, server, port=10000):
        self.server = server
        self.port = port
        self.sock_backend = None
        self.contactList = []

    def connect(self):
        self.sock_backend = zmq.Context().instance().socket(zmq.PAIR)
        self.sock_backend.connect('tcp://{}:10000'.format(self.server))

    def register_user(self):
        request = pbc.server_action()
        request.action = 'REG'
        local_user = request.contact.user.add()
        local_user.username = args.username
        local_user.ipAddr = '{}'.format(get('https://api.ipify.org').text)
        local_user.port = 10009
        request.contact.user.append(local_user)
        self.sock_backend.send(request.SerializeToString())
        print('Sent REG')
        data = self.sock_backend.recv()
        resp = pbc.server_action()
        resp.ParseFromString(data)
        if resp.action == 'ACK':
            print('Success')

    def _unpack_user_list(self, action):
        userList = []
        for user in action.contact.user:
            user_data = pbc.Contacts().user.add()
            user_data.username = user.username
            user_data.hostname = user.hostname
            user_data.isUp = user.isUp
            user_data.connectionStart = user.connectionStart
            user_data.ipAddr = user.ipAddr
            user_data.port = user.port
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
        connection_manager.request_users()
        contactList = connection_manager.getContactList()
        for user in contactList:
            print("Username: {} \t\t IP: {} \t Port: {}".format(user.username, user.ipAddr, user.port))




        #wrapper(main_app)
    except KeyboardInterrupt as e:
        pass
    except:
        raise
