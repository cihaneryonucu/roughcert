import logging
import curses
import argparse
import sys
import time
import datetime
from inquirer import Checkbox, prompt

from queue import SimpleQueue
import threading

from curses import wrapper

import message_pb2 as pbm
import chat
from connectionManager import connection_manager

logging.basicConfig(stream=sys.stdout)

def certificate_window(window, log):
    window_lines, window_cols = window.getmaxyx()
    window.bkgd(curses.A_NORMAL, curses.color_pair(2))
    window.box()
    title = " Peer certificate "
    window.addstr(0, int((window_cols  - len(title)) / 2 + 1), title)
    window.refresh()
    while True:
        log.put('Updated certificate')
        time.sleep(10)
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
    while True:
        window.addstr(bottom_line, 1, log.get())
        #window.move(bottom_line, 1)
        window.scroll(1)
        window.refresh()

def chat_window(window, log, inbox):
    window_lines, window_cols = window.getmaxyx()
    bottom_line = window_lines - 2
    window.bkgd(curses.A_NORMAL, curses.color_pair(2))
    window.scrollok(1)
    #window.box()
    title = " History "
    window.addstr(0, int((window_cols - len(title)) / 2 + 1), title)
    window.refresh()
    while True:
        if inbox.qsize() > 0: #check if we have any incoming message
            window.addstr(bottom_line, 1, inbox.get())
            window.scroll(1)
            window.refresh()
            log.put('[{}] RX - new message'.format(datetime.datetime.today().ctime()))



def input_window(window, log, outbox, inbox):
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
            inbox.put(s)
            outbox.put(s)
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
    return parser.parse_args(), parser


def main_app(stdscr, remotePeer, localUser):

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

    chat_pad = stdscr.subpad(h_splitter, v_splitter, 0, 0)
    input_pad = stdscr.subpad(window_h - h_splitter, v_splitter, h_splitter, 0)
    certificate_pad = stdscr.subpad(h_l_splitter, window_w - v_splitter, 0, v_splitter)
    logbook_pad = stdscr.subpad(window_h - h_l_splitter, window_w - v_splitter, h_l_splitter, v_splitter)


    #None arguments are for testing

    inbox = SimpleQueue()
    outbox = SimpleQueue()
    log = SimpleQueue()

    chat_history = threading.Thread(target=chat_window, args=(chat_pad, log, inbox))
    chat_history.daemon = True
    chat_history.start()
    time.sleep(0.05)

    cert_view = threading.Thread(target=certificate_window, args=(certificate_pad, log))
    cert_view.daemon = True
    cert_view.start()
    time.sleep(0.05)

    chat_sender = threading.Thread(target=input_window, args=(input_pad, log, outbox, inbox))
    chat_sender.daemon = True
    chat_sender.start()
    time.sleep(0.05)

    logbook = threading.Thread(target=logbook_window, args=(logbook_pad, log))
    logbook.daemon = True
    logbook.start()
    time.sleep(0.05)

    chat_rx = chat.Receiver(local_chat_address=localUser.get('ipAddr'), local_chat_port=localUser.get('port'), inbox=inbox)
    chat_tx = chat.Sender(remote_peer_address=remotePeer.get('ipAddr'), remote_peer_port=remotePeer.get('port'), outbox=outbox)
    
    chat_rx.run()
    chat_tx.run()

    chat_history.join()
    cert_view.join()
    chat_sender.join()
    logbook.join()



if __name__ == "__main__":
    print(" ---- Secure Chat ----")
    try:
        # check input arguments
        args, parser = input_argument()
        if args.username is None or args.port is None or args.host is None:
            parser.print_help()
            sys.exit()
        local_user = {"username" : args.username, "ipAddr" : args.host, "port" : args.port}

        print("Bootstrap: create contact entry for this user")
        connection_manager = connection_manager(server='130.237.202.97', local_user=local_user)
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
            connection_manager.remove_user()
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
        wrapper(main_app, peer, local_user)
    except KeyboardInterrupt as e:
        connection_manager.remove_user()
        pass
    except:
        raise
