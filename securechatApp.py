
import curses
import argparse
import sys
import time

import  threading

from curses import wrapper

def certificate_window(window):
    window_lines, window_cols = window.getmaxyx()
    window.bkgd(curses.A_NORMAL, curses.color_pair(2))
    window.box()
    window.refresh()
    window.addstr(0, int(window_cols / 2), "Peer certificate")
    #Validate Certificate here

def chat_window(window, display):
    window_lines, window_cols = window.getmaxyx()
    bottom_line = window_lines - 1
    window.bkgd(curses.A_NORMAL, curses.color_pair(2))
    window.scrollok(1)
    window.box()
    window.refresh()
    while (True and display is not None):
        window.box()
        window.addstr(bottom_line, 1, display.recv_string())
        window.move(bottom_line, 1)
        window.scroll(1)
        window.refresh()

def input_window(window, chat_sender):
    window.bkgd(curses.A_NORMAL, curses.color_pair(2))
    window.clear()
    window.box()
    window.refresh()
    while True:
        window.clear()
        window.box()
        window.refresh()
        s = window.getstr(1, 1).decode('utf-8')
        if s is not None and s != "" and chat_sender is not None:
            chat_sender.send_string(s)
        time.sleep(0.05)

def input_argument():
    parser = argparse.ArgumentParser(description='Secure Chat client with message self destruct')
    parser.add_argument('target',
                        type=str,
                        help='Target IP of recipient')


def main_app(stdscr):
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

    chat_pad = stdscr.subpad(h_splitter, v_splitter, 0, 0)
    input_pad = stdscr.subpad(window_h - h_splitter, v_splitter, h_splitter, 0)
    certificate_pad = stdscr.subpad(h_splitter, window_w - v_splitter, 0, v_splitter)

    #None arguments are for testing

    chat_history = threading.Thread(target=chat_window, args=(chat_pad, None))
    chat_history.daemon = True
    chat_history.start()

    cert_view = threading.Thread(target=certificate_window, args=(certificate_pad,))
    cert_view.daemon = True
    cert_view.start()

    chat_sender = threading.Thread(target=input_window, args=(input_pad, None))
    chat_sender.daemon = True
    chat_sender.start()

    chat_history.join()
    cert_view.join()
    chat_sender.join()



if __name__ == "__main__":
    print(" ---- Secure Chat ----")
    try:
        wrapper(main_app)
    except KeyboardInterrupt as e:
        pass
    except:
        raise
