import curses
import psutil
import socket
from detail_screen import DetailScreen  # New module to handle detailed view


class ServerList:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.servers = self.get_open_ports()
        self.filtered_servers = self.servers
        self.current_index = 0
        self.search_query = ""

    def get_open_ports(self):
        open_ports = []
        for conn in psutil.net_connections(kind="tcp"):
            if conn.status == psutil.CONN_LISTEN and conn.laddr:
                ip, port = conn.laddr
                process = psutil.Process(conn.pid).name() if conn.pid else "Unknown"
                open_ports.append((ip, port, process))
        return open_ports

    def display_servers(self):
        self.stdscr.clear()
        height, width = self.stdscr.getmaxyx()

        for idx, (ip, port, process) in enumerate(self.filtered_servers):
            x = 2
            y = idx + 1
            if y >= height - 2:
                break

            if idx == self.current_index:
                self.stdscr.attron(curses.color_pair(1))
                self.stdscr.addstr(y, x, f"{ip}:{port} - {process}")
                self.stdscr.attroff(curses.color_pair(1))
            else:
                self.stdscr.addstr(y, x, f"{ip}:{port} - {process}")

        self.stdscr.addstr(height - 1, 0, f"Search: {self.search_query}")
        self.stdscr.refresh()

    def filter_servers(self):
        query = self.search_query.lower()
        self.filtered_servers = [
            (ip, port, process)
            for ip, port, process in self.servers
            if query in ip.lower() or query in process.lower()
        ]
        self.current_index = 0

    def run(self):
        curses.start_color()
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)

        try:
            while True:
                self.display_servers()
                key = self.stdscr.getch()

                if key == curses.KEY_UP:
                    self.current_index = max(0, self.current_index - 1)
                elif key == curses.KEY_DOWN:
                    self.current_index = min(
                        len(self.filtered_servers) - 1, self.current_index + 1
                    )
                elif key == curses.KEY_BACKSPACE or key == 127:
                    self.search_query = self.search_query[:-1]
                    self.filter_servers()
                elif key == 10:  # Enter key
                    selected_server = self.filtered_servers[self.current_index]
                    DetailScreen(
                        self.stdscr, selected_server
                    ).run()  # Open detailed screen
                elif 32 <= key <= 126:
                    self.search_query += chr(key)
                    self.filter_servers()
                elif key == 27:  # Escape key
                    break
        except KeyboardInterrupt:
            exit(0)
