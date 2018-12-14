#!/usr/bin/env python
#
# Print port settings extension.
#
# This file is part of pySerial. https://github.com/pyserial/pyserial-terminal
# (C) 2018 Chris Liechti <cliechti@gmx.net>
#
# SPDX-License-Identifier:    BSD-3-Clause

from .api import Feature
from . import ask_for_port, print_port_settings, send_file
import serial


class Menu(Feature):
    def __init__(self, *args, hot_key='Ctrl+T'):
        super().__init__(*args)
        self.hot_key = hot_key
        self.register_hotkey(hot_key, self.handle_menu_key)

    def start(self):
        self.message('--- Quit: {} | Menu: {} | Help: {} followed by Ctrl+H ---\r\n'.format(
            self.miniterm.exit_key,
            self.hot_key,
            self.hot_key))

    def handle_menu_key(self, key_name):
        """Implement a simple menu / settings"""
        c = self.console.getkey()  # read action key
        if c == self.hot_key or c == self.miniterm.exit_key:
            # Menu/exit character again -> send itself
            self.miniterm.send_key(c)
        elif c == 'Ctrl+U':  # upload file
            send_file.SendFile(self.miniterm).execute()  # XXX
        elif c in ['Ctrl+H', 'h', 'H', '?']:  # Show help
            self.message(self.get_help_text())
        elif c == 'Ctrl+R':  # Toggle RTS
            self.serial.rts = not self.serial.rts
            self.message('--- RTS {} ---\n'.format('active' if self.serial.rts else 'inactive'))
        elif c == 'Ctrl+D':  # Toggle DTR
            self.serial.dtr = not self.serial.dtr
            self.message('--- DTR {} ---\n'.format('active' if self.serial.dtr else 'inactive'))
        elif c == 'Ctrl+B':  # toggle BREAK condition
            self.serial.break_condition = not self.serial.break_condition
            self.message('--- BREAK {} ---\n'.format('active' if self.serial.break_condition else 'inactive'))
        elif c == 'Ctrl+E':  # toggle local echo
            self.echo = not self.echo
            self.message('--- local echo {} ---\n'.format('active' if self.echo else 'inactive'))
        elif c == 'Ctrl+F':  # edit filters
            self.message('\n--- Available Filters:\n')
            self.message('\n'.join(
                '---   {:<10} = {.__doc__}'.format(k, v)
                for k, v in sorted(TRANSFORMATIONS.items())))
            self.message('\n--- Enter new filter name(s) [{}]: '.format(' '.join(self.miniterm.filters)))
            new_filters = self.ask_string().lower().split()
            if new_filters:
                for f in new_filters:
                    if f not in TRANSFORMATIONS:
                        self.message('--- unknown filter: {}'.format(repr(f)))
                        break
                else:
                    self.miniterm.filters = new_filters
                    self.miniterm.update_transformations()
            self.message('--- filters: {}\n'.format(' '.join(self.filters)))
        elif c == 'Ctrl+L':  # EOL mode
            modes = list(EOL_TRANSFORMATIONS)  # keys
            eol = modes.index(self.miniterm.eol) + 1
            if eol >= len(modes):
                eol = 0
            self.miniterm.eol = modes[eol]
            self.message('--- EOL: {} ---\n'.format(self.eol.upper()))
            self.miniterm.update_transformations()
        elif c == 'Ctrl+A':  # set encoding
            self.message('\n--- Enter new encoding name [{}]: '.format(self.input_encoding))
            new_encoding = self.ask_string().strip()
            if new_encoding:
                try:
                    codecs.lookup(new_encoding)
                except LookupError:
                    self.message('--- invalid encoding name: {}\n'.format(new_encoding))
                else:
                    self.set_rx_encoding(new_encoding)
                    self.set_tx_encoding(new_encoding)
            self.message('--- serial input encoding: {}\n'.format(self.input_encoding))
            self.message('--- serial output encoding: {}\n'.format(self.output_encoding))
        elif c == 'Tab':  # info
            self.dump_port_settings()
        elif c in 'pP':                         # P -> change port
            try:
                port = ask_for_port.AskForPort(self.miniterm).ask_for_port()
            except KeyboardInterrupt:
                port = None
            if port and port != self.serial.port:
                # reader thread needs to be shut down
                self.miniterm._stop_reader()
                # save settings
                settings = self.serial.getSettingsDict()
                try:
                    new_serial = serial.serial_for_url(port, do_not_open=True)
                    # restore settings and open
                    new_serial.applySettingsDict(settings)
                    new_serial.rts = self.serial.rts
                    new_serial.dtr = self.serial.dtr
                    new_serial.open()
                    new_serial.break_condition = self.serial.break_condition
                except Exception as e:
                    self.message('--- ERROR opening new port: {} ---\n'.format(e))
                    new_serial.close()
                else:
                    self.serial.close()
                    self.miniterm.serial = new_serial
                    self.message('--- Port changed to: {} ---\n'.format(self.serial.port))
                # and restart the reader thread
                self.miniterm._start_reader()
        elif c in 'bB':                         # B -> change baudrate
            self.message('\n--- Baudrate: ')
            backup = self.serial.baudrate
            try:
                self.serial.baudrate = int(self.ask_string().strip())
            except ValueError as e:
                self.message('--- ERROR setting baudrate: {} ---\n'.format(e))
                self.serial.baudrate = backup
            else:
                self.dump_port_settings()
        elif c == '8':                          # 8 -> change to 8 bits
            self.serial.bytesize = serial.EIGHTBITS
            self.dump_port_settings()
        elif c == '7':                          # 7 -> change to 8 bits
            self.serial.bytesize = serial.SEVENBITS
            self.dump_port_settings()
        elif c in 'eE':                         # E -> change to even parity
            self.serial.parity = serial.PARITY_EVEN
            self.dump_port_settings()
        elif c in 'oO':                         # O -> change to odd parity
            self.serial.parity = serial.PARITY_ODD
            self.dump_port_settings()
        elif c in 'mM':                         # M -> change to mark parity
            self.serial.parity = serial.PARITY_MARK
            self.dump_port_settings()
        elif c in 'sS':                         # S -> change to space parity
            self.serial.parity = serial.PARITY_SPACE
            self.dump_port_settings()
        elif c in 'nN':                         # N -> change to no parity
            self.serial.parity = serial.PARITY_NONE
            self.dump_port_settings()
        elif c == '1':                          # 1 -> change to 1 stop bits
            self.serial.stopbits = serial.STOPBITS_ONE
            self.dump_port_settings()
        elif c == '2':                          # 2 -> change to 2 stop bits
            self.serial.stopbits = serial.STOPBITS_TWO
            self.dump_port_settings()
        elif c == '3':                          # 3 -> change to 1.5 stop bits
            self.serial.stopbits = serial.STOPBITS_ONE_POINT_FIVE
            self.dump_port_settings()
        elif c in 'xX':                         # X -> change software flow control
            self.serial.xonxoff = (c == 'X')
            self.dump_port_settings()
        elif c in 'rR':                         # R -> change hardware flow control
            self.serial.rtscts = (c == 'R')
            self.dump_port_settings()
        elif c in 'qQ':                         # Q -> quit
            self.miniterm.stop()
        else:
            self.message('--- unknown menu key {} --\n'.format(c))

    def dump_port_settings(self):
        """Write current settings to console"""
        print_port_settings.PrintPortSettings(self.miniterm).execute()
        self.message('--- serial input encoding: {}\n'.format(self.miniterm.input_encoding))
        self.message('--- serial output encoding: {}\n'.format(self.miniterm.output_encoding))
        self.message('--- EOL: {}\n'.format(self.miniterm.eol.upper()))
        self.message('--- filters: {}\n'.format(' '.join(self.miniterm.filters)))

    def get_help_text(self):
        """return the help text"""
        # help text, starts with blank line!
        return """
--- pySerial-terminal ({version}) - help
---
--- {exit:8} or {menu} Q  Exit program
--- {menu:8} Menu escape key, followed by:
--- Menu keys:
---    {menu:7} Send the menu character itself to remote
---    {exit:7} Send the exit character itself to remote
---    Ctrl+I Show info
---    Ctrl+U Upload file (prompt will be shown)
---    Ctrl+A encoding
---    Ctrl+F edit filters
--- Toggles:
---    Ctrl+R RTS   Ctrl+D DTR   Ctrl+B BREAK
---    Ctrl+E echo  Ctrl+L EOL
---
--- Port settings ({menu} followed by the following):
---    p          change port
---    7 8        set data bits
---    N E O S M  change parity (None, Even, Odd, Space, Mark)
---    1 2 3      set stop bits (1, 2, 1.5)
---    b          change baud rate
---    x X        disable/enable software flow control
---    r R        disable/enable hardware flow control
""".format(version='XXX' or __version__, exit=self.miniterm.exit_key, menu=self.hot_key)
