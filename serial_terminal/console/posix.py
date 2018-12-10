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
        if ord(c) == 0x7f:
            c = u'\x08'    # map the BS key (which yields DEL) to backspace
        # XXX map escape sequences to named keys!
        return c

    def cancel(self):
        fcntl.ioctl(self.fd, termios.TIOCSTI, b'\0')

    def cleanup(self):
        termios.tcsetattr(self.fd, termios.TCSAFLUSH, self.old)

