#!/usr/bin/env python
#
# Base class for extensions of pySerial-terminal
#
# This file is part of pySerial. https://github.com/pyserial/pyserial-terminal
# (C) 2018 Chris Liechti <cliechti@gmx.net>
#
# SPDX-License-Identifier:    BSD-3-Clause


class Feature:
    """Provide a base class for extensions of the terminal application"""

    def __init__(self, miniterm):
        self.miniterm = miniterm
        self.console = miniterm.console

    @property
    def serial(self):
        return self.miniterm.serial

    def register_hotkey(self, key_name, callback):
        self.miniterm.hotkeys[key_name] = callback

    def start(self):
        """called by application when it is ready"""

    def message(self, text):
        """print a message to the console"""
        self.console.write(text.replace('\n', '\r\n'))

    def ask_string(self, question=None):
        if question:
            self.message(question)
        text = []
        while True:
            key = self.console.getkey()
            if key in ('\r', 'Enter', 'Ctrl+M'):
                break
            elif key in ('Esc', 'Crtl+C'):
                raise KeyboardInterrupt('user canceled')
            elif key == '\b':
                if text:
                    text.pop()
                    self.console.write('\b \b')
            elif len(key) == 1:
                text.append(key)
                self.console.write(key)
        self.console.write('\r\n')
        return ''.join(text)
