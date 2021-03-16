import logging
import curses
import argparse
import sys
import time
import datetime
from inquirer import Checkbox, prompt
from LogMixin import LogMixin

from collections import deque
from queue import SimpleQueue
import threading

from curses import wrapper

import message_pb2 as pbm
import chat
from connectionManager import connection_manager


class secure_chat_UI(LogMixin):
    def __init__(self, local_peer, remote_peer, crypto_info):
        self.local_peer = local_peer
        self.remote_peer = remote_peer
        self.crypto_info = crypto_info
        self.logger.debug("Started Main Window")

    def certificate_window(self, window):
        self.logger.info("Started certificate Window")
        window_lines, window_cols = window.getmaxyx()
        window.bkgd(curses.A_NORMAL, curses.color_pair(2))
        window.box()
        title = " Peer certificate "
        window.addstr(0, int((window_cols - len(title)) / 2 + 1), title)
        window.addstr(2, 1, '{}'.format(self.remote_peer))
        if user.crypto.peer_cert is not None:
            self.logger.debug("Updated window with certificate from user: {}".format(self.crypto_info.user.peer_cert))
            window.addstr(3, 1, '{}'.format(self.crypto_info.crypto.peer_cert))
        window.refresh()
        while True:
            #log.put('Updated certificate')
            time.sleep(10)
        # Validate Certificate here

    def logbook_window(self, window, log):
        self.logger.info("Started logging Window")
        window_lines, window_cols = window.getmaxyx()
        bottom_line = window_lines - 1
        window.bkgd(curses.A_NORMAL, curses.color_pair(2))
        window.scrollok(1)
        # window.box()
        title = " Logbook "
        window.addstr(0, int((window_cols - len(title)) / 2 + 1), title)
        window.refresh()
        while True:
            self.logger.debug("Added Message to logbook")
            window.addstr(bottom_line, 1, log.get())
            # window.move(bottom_line, 1)
            window.scroll(1)
            window.refresh()

    def sanitize_chat_history(self, buffer):
        require_sanitize = 0
        indexes = []
        for msg in buffer:
            if int(datetime.datetime.now().strftime("%s")) * 1000 > msg.message.timestamp_expiration and msg.sender.name == self.remote_peer.get('username'):
                indexes.append(buffer.index(msg))
                self.logger.warning('Found messages that require sanitize at {}'.format(buffer.index(msg)))
                require_sanitize = 1
        return indexes, require_sanitize

    def chat_window(self, window, log, inbox):
        self.logger.info("Started chat window")
        window_lines, window_cols = window.getmaxyx()
        bottom_line = window_lines - 2
        window.scrollok(1)
        # window.box()
        title = " History "
        window.addstr(2, int((window_cols - len(title)) / 2 + 1), title)
        window.refresh()
        message_buffer = []
        sanitized = 0
        indexes = []
        while True:
            if sanitized:
                self.logger.warning("Sanitization required - removing messages from buffer")
                for index in indexes:
                    del message_buffer[index]
                window.erase()
                title = " History "
                bottom_line = window_lines - 2
                window.addstr(2, int((window_cols - len(title)) / 2 + 1), title)
                for message in message_buffer:
                    stringToAppend = "{} - {}:\t{}".format(message.message.timestamp_generated, message.sender.name, message.message.message)
                    if message.sender.name == self.local_peer.get("username"):
                        window.addstr(bottom_line, 1, stringToAppend, curses.A_REVERSE)
                    else:
                        window.addstr(bottom_line, 1, stringToAppend)
                    window.scroll(1)
                window.refresh()

            if inbox.qsize() > 0: #check if we have any incoming message
                message = pbm.SecureChat()
                encoded_message = inbox.get()
                message.ParseFromString(encoded_message)
                message_buffer.append(message)
                stringToAppend = "{} - {}:\t{}".format(message.message.timestamp_generated, message.sender.name, message.message.message)
                if message.sender.name == self.local_peer.get("username"):
                    window.addstr(bottom_line, 1, stringToAppend, curses.A_REVERSE)
                    self.logger.debug("We received a message from the peer")
                else:
                    window.addstr(bottom_line, 1, stringToAppend)
                    self.logger.debug("We sent a message - appending it here for history")
                window.scroll(1)
                window.refresh()
                log.put('[{}] RX - new message'.format(datetime.datetime.today().ctime()))

            indexes, sanitized = self.sanitize_chat_history(message_buffer)

    def input_window(self, window, log, outbox, inbox):
        self.logger.info("Starting the user input window")
        window_lines, window_cols = window.getmaxyx()
        window.bkgd(curses.A_NORMAL, curses.color_pair(2))
        window.clear()
        window.box()
        title = " Input - User: {}".format(self.local_peer.get("username"))
        window.addstr(0, int((window_cols - len(title)) / 2), title)
        window.refresh()
        curses.curs_set(1)

        message = pbm.SecureChat()

        while True:
            window.clear()
            window.box()
            title = " Input - User: {} ".format(self.local_peer.get("username"))
            window.addstr(0, int((window_cols - len(title)) / 2), title)
            window.refresh()
            s = window.getstr(1, 1).decode('utf-8')
            if s is not None and s != "":
                self.logger.debug("Preparing message for sending...")
                message.sender.name = local_user.get('username')
                message.sender.public_ip = local_user.get('ipAddr')
                message.recepient.name = self.remote_peer.get('username')
                message.recepient.public_ip = self.remote_peer.get('ipAddr')
                message.message.message = s
                message.message.timestamp_generated = int(datetime.datetime.now().strftime("%s")) * 1000
                message.message.timestamp_expiration = int(datetime.datetime.now().strftime("%s")) * 1000 + 60 * 1000
                encodedPb = message.SerializeToString()
                inbox.put(encodedPb)
                outbox.put(encodedPb)
                log.put('[{}] TX - new message'.format(datetime.datetime.today().ctime()))
                self.logger.debug("Message put in the outbox queue")
            time.sleep(0.5)

    def main_app(self, stdscr):
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

        chat_history = threading.Thread(target=self.chat_window, args=(chat_pad, log, inbox))
        chat_history.daemon = True
        chat_history.start()

        cert_view = threading.Thread(target=self.certificate_window, args=(certificate_pad, log))
        cert_view.daemon = True
        cert_view.start()

        chat_sender = threading.Thread(target=self.input_window, args=(input_pad, log, outbox, inbox))
        chat_sender.daemon = True
        chat_sender.start()
        time.sleep(1)

        logbook = threading.Thread(target=self.logbook_window, args=(logbook_pad, log))
        logbook.daemon = True
        logbook.start()

        chat_rx = chat.Receiver(local_user=self.local_peer, crypto=self.crypto_info.crypto, inbox=inbox)
        chat_tx = chat.Sender(remote_peer=self.remote_peer, crypto=self.crypto_info.crypto, outbox=outbox)

        chat_rx.run()
        chat_tx.run()

        chat_history.join()
        cert_view.join()
        chat_sender.join()
        logbook.join()

    def launch(self):
        wrapper(self.main_app, peer, local_user)

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

if __name__ == "__main__":
    
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

        user = chat.User(local_user=local_user)
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
        app = secure_chat_UI(local_peer=local_user, remote_peer=peer, crypto_info=user)
        secure_chat_UI.launch()
    except KeyboardInterrupt as e:
        connection_manager.remove_user()
        pass
    except:
        raise
