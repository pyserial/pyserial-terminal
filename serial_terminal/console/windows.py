#!/usr/bin/env python
#
# Windows specific functions
#
# This file is part of pySerial-terminal. https://github.com/pyserial/pyserial-terminal
# (C)2002-2018 Chris Liechti <cliechti@gmx.net>
#
# SPDX-License-Identifier:    BSD-3-Clause

import ctypes, ctypes.wintypes
import codecs
import msvcrt
import sys
import os
from .base import ConsoleBase
from ..terminal import constants

try:
    chr = unichr
except NameError:
    pass

MAP_F_KEYS = {
    '\x03': 'Ctrl+2',
    '\x3b': 'F1',
    '\x3c': 'F2',
    '\x3d': 'F3',
    '\x3e': 'F4',
    '\x3f': 'F5',
    '\x40': 'F6',
    '\x41': 'F7',
    '\x42': 'F8',
    '\x43': 'F9',
    '\x44': 'F10',
    '\x47': 'KP_7',
    '\x48': 'KP_8',
    '\x49': 'KP_9',
    '\x4b': 'KP_4',
    '\x4d': 'KP_6',
    '\x4f': 'KP_1',
    '\x50': 'KP_2',
    '\x51': 'KP_3',
    '\x52': 'KP_0',
    '\x53': 'KP_Dot',
    '\x54': 'Shift+F1',
    '\x55': 'Shift+F2',
    '\x56': 'Shift+F3',
    '\x57': 'Shift+F4',
    '\x58': 'Shift+F5',
    '\x59': 'Shift+F6',
    '\x5a': 'Shift+F7',
    '\x5b': 'Shift+F8',
    '\x5c': 'Shift+F9',
    '\x5d': 'Shift+F10',
    '\x5e': 'Ctrl+F1',
    '\x5f': 'Ctrl+F2',
    '\x60': 'Ctrl+F3',
    '\x61': 'Ctrl+F4',
    '\x62': 'Ctrl+F5',
    '\x63': 'Ctrl+F6',
    '\x64': 'Ctrl+F7',
    '\x65': 'Ctrl+F8',
    '\x66': 'Ctrl+F9',
    '\x67': 'Ctrl+F10',
    '\x68': 'Alt+F1',
    '\x69': 'Alt+F2',
    '\x6a': 'Alt+F3',
    '\x6b': 'Alt+F4',
    '\x6c': 'Alt+F5',
    '\x6d': 'Alt+F6',
    '\x6e': 'Alt+F7',
    '\x6f': 'Alt+F8',
    '\x70': 'Alt+F9',
    '\x71': 'Alt+F10',
    '\x73': 'Ctrl+KP_4',
    '\x74': 'Ctrl+KP_6',
    '\x75': 'Ctrl+KP_1',
    '\x76': 'Ctrl+KP_3',
    '\x77': 'Ctrl+KP_7',
    '\x84': 'Ctrl+KP_9',
    '\x8d': 'Ctrl+KP_8',
    '\x91': 'Ctrl+KP_2',
    '\x92': 'Ctrl+KP_0',
    '\x93': 'Ctrl+KP_Dot',
    '\x94': 'Ctrl+Tab',
    '\x95': 'Ctrl+KP_Divide',
    '\x98': 'Alt+Up',
    '\x9b': 'Alt+Left',
    '\x9d': 'Alt+Right',
    '\x97': 'Alt+Home',
    '\x99': 'Alt+Page Up',
    '\x9f': 'Alt+End',
    '\xa0': 'Alt+Down',
    '\xa1': 'Alt+Page Down',
    '\xa2': 'Alt+Insert',
    '\xa3': 'Alt+Delete',
}

MAP_SPECIAL_KEYS = {
    '\x47': 'Home',
    '\x48': 'Up',
    '\x49': 'Page Up',
    '\x4b': 'Left',
    '\x4d': 'Right',
    '\x4f': 'End',
    '\x50': 'Down',
    '\x51': 'Page Down',
    '\x52': 'Insert',
    '\x53': 'Delete',
    '\x73': 'Ctrl+Right',
    '\x74': 'Ctrl+Left',
    '\x75': 'Ctrl+End',
    '\x76': 'Ctrl+Page Down',  # inconsistency, Ctrl+Page Up reports the same as F12
    '\x77': 'Ctrl+Home',
    '\x85': 'F11',
    '\x86': 'F12',
    '\x87': 'Shift+F11',
    '\x88': 'Shift+F12',
    '\x89': 'Ctrl+F11',
    '\x8a': 'Ctrl+F12',
    '\x8b': 'Alt+F11',
    '\x8c': 'Alt+F12',
    '\x8d': 'Ctrl+Up',
    '\x91': 'Ctrl+Down',
    '\x92': 'Ctrl+Insert',
    '\x93': 'Ctrl+Delete',
    '\xa2': 'Alt+Insert',
    '\xa3': 'Alt+Delete',
}


class Out(object):
    """file-like wrapper that uses os.write"""

    def __init__(self, fd):
        self.fd = fd

    def flush(self):
        pass

    def write(self, s):
        os.write(self.fd, s)


STDOUT = -11
STDERR = -12


BLACK = 0
BLUE = 1
GREEN = 2
CYAN = 3
RED = 4
MAGENTA = 5
YELLOW = 6
GREY = 7

NORMAL = 0x00
BRIGHT = 0x08


terminal_colors_to_windows_colors = {
    0: (255, GREY),
    constants.Foreground.BLACK: (7, BLACK),
    constants.Foreground.RED: (7, RED),
    constants.Foreground.GREEN: (7, GREEN),
    constants.Foreground.YELLOW: (7, YELLOW),
    constants.Foreground.BLUE: (7, BLUE),
    constants.Foreground.MAGENTA: (7, MAGENTA),
    constants.Foreground.CYAN: (7, CYAN),
    constants.Foreground.WHITE: (7, GREY),
    constants.Foreground.LIGHTBLACK: (0x0f, BLACK | BRIGHT),
    constants.Foreground.LIGHTRED: (0x0f, RED | BRIGHT),
    constants.Foreground.LIGHTGREEN: (0x0f, GREEN | BRIGHT),
    constants.Foreground.LIGHTYELLOW: (0x0f, YELLOW | BRIGHT),
    constants.Foreground.LIGHTBLUE: (0x0f, BLUE | BRIGHT),
    constants.Foreground.LIGHTMAGENTA: (0x0f, MAGENTA | BRIGHT),
    constants.Foreground.LIGHTCYAN: (0x0f, CYAN | BRIGHT),
    constants.Foreground.LIGHTWHITE: (0x0f, GREY | BRIGHT),
    constants.Background.BLACK: (7 << 4, BLACK << 4),
    constants.Background.RED: (7 << 4, RED << 4),
    constants.Background.GREEN: (7 << 4, GREEN << 4),
    constants.Background.YELLOW: (7 << 4, YELLOW << 4),
    constants.Background.BLUE: (7 << 4, BLUE << 4),
    constants.Background.MAGENTA: (7 << 4, MAGENTA << 4),
    constants.Background.CYAN: (7 << 4, CYAN << 4),
    constants.Background.WHITE: (7 << 4, GREY << 4),
    constants.Background.LIGHTBLACK: (0xf0, (BLACK | BRIGHT) << 4),
    constants.Background.LIGHTRED: (0xf0, (RED | BRIGHT) << 4),
    constants.Background.LIGHTGREEN: (0xf0, (GREEN | BRIGHT) << 4),
    constants.Background.LIGHTYELLOW: (0xf0, (YELLOW | BRIGHT) << 4),
    constants.Background.LIGHTBLUE: (0xf0, (BLUE | BRIGHT) << 4),
    constants.Background.LIGHTMAGENTA: (0xf0, (MAGENTA | BRIGHT) << 4),
    constants.Background.LIGHTCYAN: (0xf0, (CYAN | BRIGHT) << 4),
    constants.Background.LIGHTWHITE: (0xf0, (GREY | BRIGHT) << 4),
    constants.Style.BRIGHT: (0x08, BRIGHT),
    constants.Style.DIM: (0x08, NORMAL),
    constants.Style.NORMAL: (0x08, NORMAL),
}


class CONSOLE_SCREEN_BUFFER_INFO(ctypes.Structure):
    _fields_ = [
        ("dwSize", ctypes.wintypes._COORD),
        ("dwCursorPosition", ctypes.wintypes._COORD),
        ("wAttributes", ctypes.wintypes.WORD),
        ("srWindow", ctypes.wintypes.SMALL_RECT),
        ("dwMaximumWindowSize", ctypes.wintypes._COORD),
    ]


class Console(ConsoleBase):
    def __init__(self):
        super(Console, self).__init__()
        self._saved_ocp = ctypes.windll.kernel32.GetConsoleOutputCP()
        self._saved_icp = ctypes.windll.kernel32.GetConsoleCP()
        ctypes.windll.kernel32.SetConsoleOutputCP(65001)
        ctypes.windll.kernel32.SetConsoleCP(65001)
        #~ self.output = colorama.AnsiToWin32(codecs.getwriter('UTF-8')(Out(sys.stdout.fileno()), 'replace')).stream
        self.output = codecs.getwriter('UTF-8')(Out(sys.stdout.fileno()), 'replace')
        # the change of the code page is not propagated to Python, manually fix it
        sys.stderr = codecs.getwriter('UTF-8')(Out(sys.stderr.fileno()), 'replace')
        sys.stdout = self.output
        self.output.encoding = 'UTF-8'  # needed for input
        self.handle = ctypes.windll.kernel32.GetStdHandle(STDOUT)
        self.console_handle = ctypes.windll.kernel32.GetConsoleWindow()

    def __del__(self):
        ctypes.windll.kernel32.SetConsoleTextAttribute(self.handle, GREY)
        ctypes.windll.kernel32.SetConsoleOutputCP(self._saved_ocp)
        ctypes.windll.kernel32.SetConsoleCP(self._saved_icp)

    def getkey(self):
        """read from console, converting special keys to escape sequences"""
        while True:
            z = msvcrt.getwch()
            if z in chr(0):     # functions keys
                code = msvcrt.getwch()
                try:
                    return MAP_F_KEYS[code]
                except KeyError:
                    return 'unknown F key {!r} {:02x}'.format(code, ord(code))
            elif z in chr(0xe0):    # cursor keys, home/end
                code = msvcrt.getwch()
                try:
                    return MAP_SPECIAL_KEYS[code]
                except KeyError:
                    return 'unknown special key {!r} {:02x}'.format(code, ord(code))
            else:
                return z

    def cancel(self):
        # CancelIo, CancelSynchronousIo do not seem to work when using
        # getwch, so instead, send a key to the window with the console
        ctypes.windll.user32.PostMessageA(self.console_handle, 0x100, 0x0d, 0)

    def write_bytes(self, byte_str):
        self.byte_output.write(byte_str)
        self.byte_output.flush()

    def write(self, text):
        chars_written = ctypes.wintypes.DWORD()
        ctypes.windll.kernel32.WriteConsoleW(
            self.handle,
            ctypes.c_wchar_p(text),
            len(text),
            ctypes.byref(chars_written),
            None)

    def set_ansi_color(self, colorcodes):
        """set foreground text"""
        attrs = 0
        for colorcode in colorcodes:
            mask, code = terminal_colors_to_windows_colors[colorcode]
            # print(attrs, bin((~mask) & 0xffff), code)
            attrs = (attrs & ~mask) | code
        # print('xxx', self.handle, attrs)
        ctypes.windll.kernel32.SetConsoleTextAttribute(self.handle, attrs)

    def get_position_and_size(self):
        info = CONSOLE_SCREEN_BUFFER_INFO()
        ctypes.windll.kernel32.GetConsoleScreenBufferInfo(self.handle, ctypes.byref(info))
        # print('getpos', info.dwCursorPosition.X, info.dwCursorPosition.Y, info.dwSize.X, info.dwSize.Y)
        return info.dwCursorPosition.X, info.dwCursorPosition.Y, info.dwSize.X, info.dwSize.Y

    def set_cursor_position(self, x, y):
        # print('setpos', x, y)
        ctypes.windll.kernel32.SetConsoleCursorPosition(
            self.handle,
            ctypes.wintypes._COORD(x, y))

    def erase(self, x, y, width, height, selective=False):
        # print('erase', x, y, width, height, selective)
        chars_written = ctypes.wintypes.DWORD()
        spaces = ctypes.c_wchar_p(' ' * width)
        attrs = (ctypes.wintypes.WORD * width)()
        for _y in range(y, y + height):
            ctypes.windll.kernel32.WriteConsoleOutputCharacterW(
                self.handle,
                spaces,
                width,
                ctypes.wintypes._COORD(x, _y),  # dwWriteCoord
                ctypes.byref(chars_written))
            if not selective:
                ctypes.windll.kernel32.WriteConsoleOutputAttribute(
                    self.handle,
                    ctypes.byref(attrs),
                    width,
                    ctypes.wintypes._COORD(x, _y),  # dwWriteCoord
                    ctypes.byref(chars_written))


if __name__ == "__main__":
    # test code to show what key codes are generated
    console = Console()
    while True:
        key = console.getkey()
        print(repr(key))
        if key == '\x04':  # exit with CTRL+D
            break
