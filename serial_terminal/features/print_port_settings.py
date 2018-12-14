#!/usr/bin/env python
#
# Print port settings extension.
#
# This file is part of pySerial. https://github.com/pyserial/pyserial-terminal
# (C) 2018 Chris Liechti <cliechti@gmx.net>
#
# SPDX-License-Identifier:    BSD-3-Clause

from .api import Feature
import serial


class PrintPortSettings(Feature):

    def execute(self):
        """Write current settings to sys.stderr"""
        self.message("\n--- Settings: {p.name}  {p.baudrate},{p.bytesize},{p.parity},{p.stopbits}\n".format(
            p=self.serial))
        self.message('--- RTS: {:8}  DTR: {:8}  BREAK: {:8}\n'.format(
            ('active' if self.serial.rts else 'inactive'),
            ('active' if self.serial.dtr else 'inactive'),
            ('active' if self.serial.break_condition else 'inactive')))
        try:
            self.message('--- CTS: {:8}  DSR: {:8}  RI: {:8}  CD: {:8}\n'.format(
                ('active' if self.serial.cts else 'inactive'),
                ('active' if self.serial.dsr else 'inactive'),
                ('active' if self.serial.ri else 'inactive'),
                ('active' if self.serial.cd else 'inactive')))
        except serial.SerialException:
            # on RFC 2217 ports, it can happen if no modem state notification was
            # yet received. ignore this error.
            pass
        self.message('--- software flow control: {}\n'.format('active' if self.serial.xonxoff else 'inactive'))
        self.message('--- hardware flow control: {}\n'.format('active' if self.serial.rtscts else 'inactive'))
        # self.message('--- serial input encoding: {}\n'.format(self.input_encoding))
        # self.message('--- serial output encoding: {}\n'.format(self.output_encoding))
        # self.message('--- EOL: {}\n'.format(self.eol.upper()))
        # self.message('--- filters: {}\n'.format(' '.join(self.filters)))
