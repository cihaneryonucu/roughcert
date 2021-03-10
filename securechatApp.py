import logging
import curses
import argparse
import sys
import time
import datetime
from inquirer import Checkbox, prompt
import textwrap

from collections import deque
from queue import SimpleQueue
import threading

from curses import wrapper

import message_pb2 as pbm
import chat
from connectionManager import connection_manager


class Logger:
 
    def __init__(self, filename):
        self.console = sys.stdout
        self.file = open(filename, 'w')
 
    def write(self, message):
        self.console.write(message)
        self.file.write(message)
 
    def flush(self):
        self.console.flush()
        self.file.flush()

def certificate_window(window, log, remotePeer):
    window_lines, window_cols = window.getmaxyx()
    window.bkgd(curses.A_NORMAL, curses.color_pair(2))
    window.box()
    title = " Peer certificate "
    window.addstr(0, int((window_cols - len(title)) / 2 + 1), title)
    window.addstr(2, 1, '{}'.format(remotePeer))

    window.refresh()
    while True:
        #log.put('Updated certificate')
        time.sleep(10)
    # Validate Certificate here

def logbook_window(window, log):
    window_lines, window_cols = window.getmaxyx()
    bottom_line = window_lines - 1
    window.bkgd(curses.A_NORMAL, curses.color_pair(2))
    window.scrollok(1)
    # window.box()
    title = " Logbook "
    window.addstr(0, int((window_cols - len(title)) / 2 + 1), title)
    window.refresh()
    while True:
        window.addstr(bottom_line, 1, log.get())
        # window.move(bottom_line, 1)
        window.scroll(1)
        window.refresh()

def sanitize_chat_history(buffer, remotePeer):
    require_sanitize = 0
    indexes = []
    for msg in buffer:
        if int(datetime.datetime.now().strftime("%s")) * 1000 > msg.message.timestamp_expiration and msg.sender.name == remotePeer.get('username'):
            indexes.append(buffer.index(msg))
            require_sanitize = 1
    return indexes, require_sanitize

def chat_window(window, log, inbox, localUser, remotePeer):
    window_lines, window_cols = window.getmaxyx()
    bottom_line = window_lines - 2
    window.scrollok(1)
    # window.box()
    title = " History "
    window.addstr(2, int((window_cols - len(title)) / 2 + 1), title)
    window.refresh()

    message_buffer = []
    ready_to_print = 0

    sanitized = 0
    indexes = []


    while True:

        if sanitized:
            for index in indexes:
                del message_buffer[index]
            window.erase()
            title = " History "
            bottom_line = window_lines - 2
            window.addstr(2, int((window_cols - len(title)) / 2 + 1), title)
            for message in message_buffer:
                stringToAppend = "{} - {}:\t{}".format(message.message.timestamp_generated, message.sender.name, message.message.message)
                if message.sender.name == localUser.get("username"):
                    window.addstr(bottom_line, 1, stringToAppend, curses.A_REVERSE)
                else:
                    window.addstr(bottom_line, 1, stringToAppend)
                window.scroll(1)
            window.refresh()
            sanitized = 0
            indexes = []
            
        if inbox.qsize() > 0: #check if we have any incoming message
            message = pbm.SecureChat()
            encoded_message = inbox.get()
            message.ParseFromString(encoded_message)
            message_buffer.append(message)
            stringToAppend = "{} - {}:\t{}".format(message.message.timestamp_generated, message.sender.name, message.message.message)
            if message.sender.name == localUser.get("username"):
                window.addstr(bottom_line, 1, stringToAppend, curses.A_REVERSE)
            else:
                window.addstr(bottom_line, 1, stringToAppend)
            window.scroll(1)
            window.refresh()
            log.put('[{}] RX - new message'.format(datetime.datetime.today().ctime()))

        indexes, sanitized = sanitize_chat_history(message_buffer, remotePeer)
         



def input_window(window, log, outbox, inbox, localUser, remotePeer):
    window_lines, window_cols = window.getmaxyx()
    window.bkgd(curses.A_NORMAL, curses.color_pair(2))
    window.clear()
    window.box()
    title = " Input - User: {}".format(localUser.get("username"))
    window.addstr(0, int((window_cols - len(title)) / 2), title)
    window.refresh()
    curses.curs_set(1)

    message = pbm.SecureChat()

    while True:
        window.clear()
        window.box()
        title = " Input - User: {} ".format(localUser.get("username"))
        window.addstr(0, int((window_cols - len(title)) / 2), title)
        window.refresh()
        s = window.getstr(1, 1).decode('utf-8')
        if s is not None and s != "":
            message.sender.name = local_user.get('username')
            message.sender.public_ip = local_user.get('ipAddr')
            message.recepient.name = remotePeer.get('username')
            message.recepient.public_ip = remotePeer.get('ipAddr')
            message.message.message = s
            message.message.timestamp_generated = int(datetime.datetime.now().strftime("%s")) * 1000 
            message.message.timestamp_expiration = int(datetime.datetime.now().strftime("%s")) * 1000 + 60 * 1000
            encodedPb = message.SerializeToString()
            inbox.put(encodedPb)
            outbox.put(encodedPb)
            log.put('[{}] TX - new message'.format(datetime.datetime.today().ctime()))
        time.sleep(0.5)

def input_argument():
    parser = argparse.ArgumentParser(description='Secure Chat client with message self destruct')
    parser.add_argument('--username',
                        type=str,
                        help='Username of sender')
    parser.add_argument('--port',
                        type=str,
                        help='port of sender')
    parser.add_argument('--host',
                        type=str,
                        help='ip of the host')
    parser.add_argument('--remote',
                        type=str,
                        help='ip of the server')
    parser.add_argument('--key',
                        type=str,
                        help='Specify certificate/key basename')
    return parser.parse_args(), parser


def main_app(stdscr, remotePeer, localUser, user):

    ### curses set up

    #Clear screen
    stdscr.clear()

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

    chat_pad = curses.newwin(h_splitter, v_splitter, 0, 0)
    input_pad = curses.newwin(window_h - h_splitter, v_splitter, h_splitter, 0)
    certificate_pad = curses.newwin(h_l_splitter, window_w - v_splitter, 0, v_splitter)
    logbook_pad = curses.newwin(window_h - h_l_splitter, window_w - v_splitter, h_l_splitter, v_splitter)


    #None arguments are for testing

    inbox = SimpleQueue()
    outbox = SimpleQueue()
    log = SimpleQueue()

    chat_history = threading.Thread(target=chat_window, args=(chat_pad, log, inbox, localUser, remotePeer))
    chat_history.daemon = True
    chat_history.start()
    time.sleep(1)

    cert_view = threading.Thread(target=certificate_window, args=(certificate_pad, log, remotePeer))
    cert_view.daemon = True
    cert_view.start()
    time.sleep(1)

    chat_sender = threading.Thread(target=input_window, args=(input_pad, log, outbox, inbox, localUser, remotePeer))
    chat_sender.daemon = True
    chat_sender.start()
    time.sleep(1)

    logbook = threading.Thread(target=logbook_window, args=(logbook_pad, log))
    logbook.daemon = True
    logbook.start()
    time.sleep(1)

    # if not user.isInitiator:
    #     user.set_remote_address(remotePeer.get('ipAddr'))
    #     user.force_request()

    chat_rx = chat.Receiver(local_user=localUser, crypto=user.crypto, inbox=inbox)
    chat_tx = chat.Sender(remote_peer=localUser, crypto=user.crypto, outbox=outbox)

    chat_rx.run()
    chat_tx.run()

    chat_history.join()
    cert_view.join()
    chat_sender.join()
    logbook.join()



if __name__ == "__main__":
    
    path = 'stdout.log'
    sys.stdout = Logger(path)
    print(" ---- Secure Chat ----")
    try:
        # check input arguments
        args, parser = input_argument()
        if args.username is None or args.port is None or args.host is None or args.key is None:
            parser.print_help()
            sys.exit()

        local_user = {"username" : args.username, "ipAddr" : args.host, "port" : args.port, "keyBase" : args.key}
        if args.remote is None or args.remote == '':
            remote = '130.237.202.97'
        else:
            remote = args.remote

        print("Bootstrap: create contact entry for this user")
        connection_manager = connection_manager(server=remote, local_user=local_user)
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
            if answer.get('Check for peers') == ['yes']:
                connection_manager.request_users()
                contactList = connection_manager.getContactList()
            else:
                break

        if not contactList:
            print("I mean... you gotta be talking to someboby right? bye...")
            connection_manager.remove_user()
            sys.exit(0)

        user = chat.User(localUser=local_user)
        user.run()

        questions = [
            Checkbox('Peers',
                     message='Select a peer to connect to',
                     choices=contactList)
        ]
        answer = prompt(questions)
        peer = answer.get('Peers')[0]

        print('User selected: {}'.format(peer))
        input()
        if not user.isInitiator:
            print('We are initiators')
            user.set_remote_address(peer.get('ipAddr'))
            user.force_request()

        print('Established pair keys')
        input()
        wrapper(main_app, peer, local_user, user)
    except KeyboardInterrupt as e:
        connection_manager.remove_user()
        pass
    except:
        raise
