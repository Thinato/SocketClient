#!/usr/bin/python3
import curses
from server_list import ServerList

def main(stdscr):
    # Initialize curses and server list
    stdscr.clear()
    server_list = ServerList(stdscr)
    server_list.run()

if __name__ == "__main__":
    curses.wrapper(main)
