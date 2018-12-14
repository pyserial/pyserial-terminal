#!/usr/bin/env python
#
# Write a info message at startup.
#
# This file is part of pySerial. https://github.com/pyserial/pyserial-terminal
# (C) 2018 Chris Liechti <cliechti@gmx.net>
#
# SPDX-License-Identifier:    BSD-3-Clause

from .api import Feature


class StartupMessage(Feature):
    def start(self):
        self.miniterm.console.write('--- pySerial-terminal on {p.name}  {p.baudrate},{p.bytesize},{p.parity},{p.stopbits} ---\r\n'.format(
            p=self.serial))
