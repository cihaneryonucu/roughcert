
import curses
import argparse
import sys
import time
import datetime
import zmq

import threading

from curses import wrapper

import message_pb2

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
    parser.add_argument('--target',
                        type=str,
                        help='Target IP of recipient')
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



if __name__ == "__main__":
    print(" ---- Secure Chat ----")
    try:
        # check input arguments
        args = input_argument()
        if args.target is None:
            sys.exit('Error - Missing TARGET ip')
        wrapper(main_app)
    except KeyboardInterrupt as e:
        pass
    except:
        raise
