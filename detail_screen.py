# detail_screen.py
import curses
import socket


class DetailScreen:
    def __init__(self, stdscr, server):
        self.stdscr = stdscr
        self.server = server
        self.messages = []  # Store (message, is_sent) tuples
        self.input_buffer = ""
        self.is_hex = True  # Toggle between hex and UTF-8 encoding
        self.skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.messages.append(("Connecting to " + str(server), False))
        try:
            self.skt.connect(server[:2])
            self.messages.append(("Connected", False))
        except ConnectionRefusedError:
            self.messages.append(("Connection refused", False))

    def display_header(self):
        ip, port, process = self.server
        self.stdscr.addstr(0, 0, f"Connection: {ip}:{port} - {process}", curses.A_BOLD)
        self.stdscr.addstr(1, 0, "-" * 80)

    def display_messages(self):
        height, width = self.stdscr.getmaxyx()
        for idx, (msg, is_sent) in enumerate(
            self.messages[-(height - 5) :]
        ):  # Display last N messages
            color = curses.color_pair(2) if is_sent else curses.color_pair(3)
            self.stdscr.addstr(2 + idx, 0, msg, color)

    def display_input(self):
        height, _ = self.stdscr.getmaxyx()
        mode = "Hexadecimal" if self.is_hex else "UTF-8"
        self.stdscr.addstr(height - 2, 0, f"Mode: {mode} | Input: {self.input_buffer}")
        self.stdscr.refresh()

    def send_data(self, data: bytes):
        self.skt.send(data)

    def run(self):
        curses.start_color()
        curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)  # Sent messages
        curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_BLACK)  # Received messages

        try:
            while True:
                self.stdscr.clear()
                self.display_header()
                self.display_messages()
                self.display_input()

                key = self.stdscr.getch()
                if key == 27:  # Escape key to exit
                    break
                elif key == curses.KEY_BACKSPACE or key == 127:
                    self.input_buffer = self.input_buffer[:-1]
                elif key == 10:  # Enter key to send message
                    if self.is_hex:
                        try:
                            byte_data = bytes.fromhex(
                                self.input_buffer.replace(",", "")
                            )
                            self.messages.append((f"Sent: {byte_data}", True))
                            self.send_data(byte_data)
                        except ValueError:
                            self.messages.append(("Invalid hex input", True))
                    else:
                        self.messages.append((f"Sent: {self.input_buffer}", True))
                        self.send_data(self.input_buffer.encode())
                    self.input_buffer = ""
                elif key == ord("!"):  # Toggle encoding mode
                    self.is_hex = not self.is_hex
                elif 32 <= key <= 126:  # Printable characters
                    self.input_buffer += chr(key)
        except KeyboardInterrupt:
            exit(0)
