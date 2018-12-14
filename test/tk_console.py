#!/usr/bin/env python3
#
# Python 3+ only tkinter terminal widget wrapper: show the output of a
# console program in the widget.
#
# This file is part of pySerial-terminal. https://github.com/pyserial/pyserial-terminal
# (C) 2018 Chris Liechti <cliechti@gmx.net>
#
# SPDX-License-Identifier:    BSD-3-Clause
import pathlib
import subprocess
import sys

import tkinter as tk
from tkinter import ttk

sys.path.append(str(pathlib.Path(__file__).parent.parent))
from serial_terminal.console import tk_widget
from serial_terminal.terminal.escape_decoder import EscapeDecoder
from serial_terminal.emulation.simple import SimpleTerminal

import serial

def main():
    root = tk.Tk()
    root.title('pySerial-Terminal tk_widget test')
    console = tk_widget.Console(root)
    # console.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
    console.pack()
    terminal = SimpleTerminal(console)
    decoder = EscapeDecoder(terminal)

    p = subprocess.Popen([sys.executable] + sys.argv[1:], stdout=subprocess.PIPE)
    # p.stdin.close()
    while True:
        data = p.stdout.read(4096)
        if not data:
            break
        for byte in serial.iterbytes(data):
            decoder.handle(byte)
        root.update_idletasks()
        root.update()

    root.mainloop()


if __name__ == "__main__":
    main()
