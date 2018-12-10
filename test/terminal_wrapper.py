#!/usr/bin/env python
#
# Test support to run external tools and use our terminal emulation.
#
# This file is part of pySerial-terminal. https://github.com/pyserial/pyserial-terminal
# (C)2002-2018 Chris Liechti <cliechti@gmx.net>
#
# SPDX-License-Identifier:    BSD-3-Clause

import subprocess
import sys
import pathlib

sys.path.append(str(pathlib.Path(__file__).parent.parent))
from serial_terminal.console import Console
from serial_terminal.terminal.escape_decoder import EscapeDecoder
from serial_terminal.emulation.simple import SimpleTerminal


def main():
    terminal = SimpleTerminal(Console())
    decoder = EscapeDecoder(terminal)
    p = subprocess.Popen([sys.executable] + sys.argv[1:], stdout=subprocess.PIPE)
    # p.stdin.close()
    while True:
        data = p.stdout.read(1)
        if not data:
            break
        decoder.handle(data)
    # sys.stdout.buffer.write(b'\n')


if __name__ == "__main__":
    main()
