#!/usr/bin/env python
#
# Send file contents extension
#
# This file is part of pySerial. https://github.com/pyserial/pyserial-terminal
# (C) 2018 Chris Liechti <cliechti@gmx.net>
#
# SPDX-License-Identifier:    BSD-3-Clause

from .api import Feature

class SendFile(Feature):
    # {'menu_key': 'Ctrl+U'}

    def execute(self):
        self.message('\n--- File to upload: ')
        with self.console:
            filename = self.ask_string().rstrip('\r\n')
            if filename:
                try:
                    with open(filename, 'rb') as f:
                        self.message('--- Sending file {} ---\n'.format(filename))
                        while True:
                            block = f.read(1024)
                            if not block:
                                break
                            self.serial.write(block)
                            # Wait for output buffer to drain.
                            self.serial.flush()
                            self.message('.')   # Progress indicator.
                    self.message('\n--- File {} sent ---\n'.format(filename))
                except IOError as e:
                    self.message('--- ERROR opening file {}: {} ---\n'.format(filename, e))
