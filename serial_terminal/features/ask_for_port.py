#!/usr/bin/env python
#
# Print port settings extension.
#
# This file is part of pySerial. https://github.com/pyserial/pyserial-terminal
# (C) 2018 Chris Liechti <cliechti@gmx.net>
#
# SPDX-License-Identifier:    BSD-3-Clause

from .api import Feature
from serial.tools.list_ports import comports


class AskForPort(Feature):
    def ask_for_port(self):
        """\
        Show a list of ports and ask the user for a choice. To make selection
        easier on systems with long device names, also allow the input of an
        index.
        """
        self.message('\n--- Available ports:\n')
        ports = []
        for n, (port, desc, hwid) in enumerate(sorted(comports()), 1):
            self.message('--- {:2}: {:20} {}\n'.format(n, port, desc))
            ports.append(port)
        while True:
            port = self.ask_string('--- Enter port index or full name: ')
            try:
                index = int(port) - 1
                if not 0 <= index < len(ports):
                    self.message('--- Invalid index!\n')
                    continue
            except ValueError:
                pass
            else:
                port = ports[index]
            return port
