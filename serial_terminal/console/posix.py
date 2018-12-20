#!/usr/bin/env python
#
# Posix specific functions
#
# This file is part of pySerial-terminal. https://github.com/pyserial/pyserial-terminal
# (C)2002-2018 Chris Liechti <cliechti@gmx.net>
#
# SPDX-License-Identifier:    BSD-3-Clause

from .base import ConsoleBase

import atexit
import fcntl
import sys
import termios
import codecs


MAP_CONTROL_KEYS = {
    '\x00': 'Ctrl+Space',
    '\x01': 'Ctrl+A',
    '\x02': 'Ctrl+B',
    '\x03': 'Ctrl+C',
    '\x04': 'Ctrl+D',
    '\x05': 'Ctrl+E',
    '\x06': 'Ctrl+F',
    '\x07': 'Ctrl+G',
    '\x08': 'Ctrl+H',
    '\x09': 'Tab',  # 'Ctrl+I',
    '\x0a': 'Ctrl+J',
    '\x0b': 'Ctrl+K',
    '\x0c': 'Ctrl+L',
    '\x0d': 'Ctrl+M',
    '\x0e': 'Ctrl+N',
    '\x0f': 'Ctrl+O',
    '\x10': 'Ctrl+P',
    '\x11': 'Ctrl+Q',
    '\x12': 'Ctrl+R',
    '\x13': 'Ctrl+S',
    '\x14': 'Ctrl+T',
    '\x15': 'Ctrl+U',
    '\x16': 'Ctrl+V',
    '\x17': 'Ctrl+W',
    '\x18': 'Ctrl+X',
    '\x19': 'Ctrl+Y',
    '\x1a': 'Ctrl+Z',
    '\x1b': 'Esc',  # 'Ctrl+[',
    '\x1c': 'Ctrl+\\',
    '\x1d': 'Ctrl+]',
    '\x1e': 'Ctrl+^',
    '\x1f': 'Ctrl+_',
}

CSI_CODES = {
    'H': 'Home',
    'F': 'End',
    '1;2H': 'Shift+Home',
    '1;2F': 'Shift+End',
    '1;3H': 'Alt+Home',
    '1;3F': 'Alt+End',
    '1;5H': 'Ctrl+Home',
    '1;5F': 'Ctrl+End',
    '2~': 'Insert',
    '3~': 'Delete',
    '5~': 'Page Up',
    '6~': 'Page Down',
    '2;2~': 'Shift+Insert',
    '3;2~': 'Shift+Delete',
    '5;2~': 'Shift+Page Up',
    '6;2~': 'Shift+Page Down',
    '2;3~': 'Alt+Insert',
    '3;3~': 'Alt+Delete',
    '5;3~': 'Alt+Page Up',
    '6;3~': 'Alt+Page Down',
    '2;5~': 'Ctrl+Insert',
    '3;5~': 'Ctrl+Delete',
    '5;5~': 'Ctrl+Page Up',
    '6;5~': 'Ctrl+Page Down',
    '15~': 'F5',
    '16~': 'F6',
    '17~': 'F7',
    '18~': 'F8',
    '20~': 'F9',
    '21~': 'F10',
    '23~': 'F11',
    '24~': 'F12',
    '1;2P': 'Shift+F1',
    '1;2Q': 'Shift+F2',
    '1;2R': 'Shift+F3',
    '1;2S': 'Shift+F4',
    '15;2~': 'Shift+F5',
    '16;2~': 'Shift+F6',
    '17;2~': 'Shift+F7',
    '18;2~': 'Shift+F8',
    '20;2~': 'Shift+F9',
    '21;2~': 'Shift+F10',
    '23;2~': 'Shift+F11',
    '24;2~': 'Shift+F12',
    '1;3P': 'Alt+F1',
    '1;3Q': 'Alt+F2',
    '1;3R': 'Alt+F3',
    '1;3S': 'Alt+F4',
    '15;3~': 'Alt+F5',
    '16;3~': 'Alt+F6',
    '17;3~': 'Alt+F7',
    '18;3~': 'Alt+F8',
    '20;3~': 'Alt+F9',
    '21;3~': 'Alt+F10',
    '23;3~': 'Alt+F11',
    '24;3~': 'Alt+F12',
    '1;5P': 'Ctrl+F1',
    '1;5Q': 'Ctrl+F2',
    '1;5R': 'Ctrl+F3',
    '1;5S': 'Ctrl+F4',
    '15;5~': 'Ctrl+F5',
    '16;5~': 'Ctrl+F6',
    '17;5~': 'Ctrl+F7',
    '18;5~': 'Ctrl+F8',
    '20;5~': 'Ctrl+F9',
    '21;5~': 'Ctrl+F10',
    '23;5~': 'Ctrl+F11',
    '24;5~': 'Ctrl+F12',
    'A': 'Up',
    'B': 'Down',
    'C': 'Right',
    'D': 'Left',
    '1;2A': 'Shift+Up',
    '1;2B': 'Shift+Down',
    '1;2C': 'Shift+Right',
    '1;2D': 'Shift+Left',
    '1;3A': 'Alt+Up',
    '1;3B': 'Alt+Down',
    '1;3C': 'Alt+Right',
    '1;3D': 'Alt+Left',
    '1;5A': 'Ctrl+Up',
    '1;5B': 'Ctrl+Down',
    '1;5C': 'Ctrl+Right',
    '1;5D': 'Ctrl+Left',
    'E': 'KP_5',
    '1;2E': 'Shift+KP_5',
    '1;3E': 'Alt+KP_5',
    '1;5E': 'Ctrl+KP_5',
    'Z': 'Shift+Tab',
}

SS3_CODES = {
    'P': 'F1',
    'Q': 'F2',
    'R': 'F3',
    'S': 'F4',
}


class Console(ConsoleBase):
    def __init__(self):
        super(Console, self).__init__()
        self.fd = sys.stdin.fileno()
        self.old = termios.tcgetattr(self.fd)
        atexit.register(self.cleanup)
        if sys.version_info < (3, 0):
            self.enc_stdin = codecs.getreader(sys.stdin.encoding)(sys.stdin)
        else:
            self.enc_stdin = sys.stdin

    def setup(self):
        new = termios.tcgetattr(self.fd)
        new[3] = new[3] & ~termios.ICANON & ~termios.ECHO & ~termios.ISIG
        new[6][termios.VMIN] = 1
        new[6][termios.VTIME] = 0
        termios.tcsetattr(self.fd, termios.TCSANOW, new)

    def getkey(self):
        c = self.enc_stdin.read(1)
        if c == '\x1b':
            return self.handle_esc()
        elif c and c < '\x20':
            return MAP_CONTROL_KEYS[c]
        elif c == '\x7f':
            return 'Remove'
        else:
            return c

    def handle_esc(self):
        c = self.enc_stdin.read(1)  # should read with timeout so that single ESC press can be handled
        if c == '[':  # CSI
            return self.handle_csi()
        elif c == 'O':  # SS3
            return self.handle_SS3()
        elif c == '\x1b':  # ESC
            return 'Esc'
        else:
            return 'unknown escape {!r}'.format(c)

    def handle_csi(self):
        parameter = []
        while True:
            c = self.enc_stdin.read(1)
            if '0' <= c <= '9' or c == ';':
                parameter.append(c)
            else:
                try:
                    return CSI_CODES[''.join(parameter + [c])]
                except KeyError:
                    return 'unknown CSI {}{}'.format(''.join(parameter), c)

    def handle_SS3(self):
        c = self.enc_stdin.read(1)
        try:
            return SS3_CODES[c]
        except KeyError:
            return 'unknown SS3 code {}'.format(c)


    def cancel(self):
        fcntl.ioctl(self.fd, termios.TIOCSTI, b'\0')

    def cleanup(self):
        termios.tcsetattr(self.fd, termios.TCSAFLUSH, self.old)

    def set_ansi_color(self, colorcodes):
        """set color/intensity for next write(s)"""

    def get_position_and_size(self):
        """get cursor position (zero based) and window size"""  # XXX buffer size on windows :/

    def set_cursor_position(self, x, y):
        """set cursor position (zero based)"""
        # print('setpos', x, y)

    def move_or_scroll_down(self):
        """move cursor down, extend and scroll if needed"""
        self.write('\n')

    def move_or_scroll_up(self):
        """move cursor up, extend and scroll if needed"""
        # not entirely correct
        x, y, w, h = self.get_position_and_size()
        self.set_cursor_position(x, y - 1)

    def erase(self, x, y, width, height, selective=False):
        """erase rectangular area"""
        # print('erase', x, y, width, height, selective)


if __name__ == "__main__":
    # test code to show what key codes are generated
    console = Console()
    console.setup()
    while True:
        key = console.getkey()
        print(repr(key))
        if key == 'Ctrl+D':
            break
