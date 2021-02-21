
import curses
import argparse
import sys
import time

from curses import wrapper

def certificate_window(window, display):
    window_lines, window_cols = window.getmaxyx()
    bottom_line = window_lines - 1
    window.bkgd(curses.A_NORMAL, curses.color_pair(2))
    window.scrollok(1)
    #Validate Certificate here

def chat_window(window, display):
    window_lines, window_cols = window.getmaxyx()
    bottom_line = window_lines - 1
    window.bkgd(curses.A_NORMAL, curses.color_pair(2))
    window.scrollok(1)
    while True:
        # alternate color pair used to visually check how frequently this loop runs
        # to tell when user input is blocking
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
        if s is not None and s != "":
            chat_sender.send_string(s)
        # need to do sleep here...
        # if bottom window gets down to `window.getstr...` while top window is setting up,
        # it registers a bunch of control characters as the user's input
        time.sleep(0.005)

def input_argument():
    parser = argparse.ArgumentParser(description='Secure Chat client with message self destruct')
    parser.add_argument('target',
                        type=str,
                        help='Target IP of recipient')


def main_app(stdscr):
    ### curses set up
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLACK)
    # ensure that user input is echoed to the screen
    curses.echo()
    curses.curs_set(0)

    window_w = curses.LINES
    window_h = curses.COLS
    print(window_w, window_h)
    h_splitter = int(window_h * 0.8)
    v_splitter = int(window_w * 0.65)

    chat_pad = stdscr.subpad(h_splitter, v_splitter, 0, 0)
    input_pad = stdscr.subpad(window_h - h_splitter, window_w, h_splitter, 0)
    certificate_pad = stdscr.subpad(h_splitter, window_w - v_splitter, 0, v_splitter)




if __name__ == "__main__":
    print(" ---- Secure Chat ----")
    try:
        wrapper(main_app)
    except KeyboardInterrupt as e:
        pass
    except:
        raise
