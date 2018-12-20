#!/usr/bin/env python
#
# pySerial-terminal
#
# This file is part of pySerial. https://github.com/pyserial/pyserial-terminal
# (C) 2002-2018 Chris Liechti <cliechti@gmx.net>
#
# SPDX-License-Identifier:    BSD-3-Clause

import codecs
import os
import sys
import threading
import traceback

from .console import Console
from .terminal.escape_decoder import EscapeDecoder
from .terminal.escape_encoder import EscapeEncoder
from .emulation.simple import SimpleTerminal
from .features import menu, ask_for_port, startup_message

import serial
from serial.tools import hexlify_codec
from . import __version__

# pylint: disable=wrong-import-order,wrong-import-position

codecs.register(lambda c: hexlify_codec.getregentry() if c == 'hexlify' else None)

try:
    unichr
except NameError:
    # pylint: disable=redefined-builtin,invalid-name
    unichr = chr


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class Transform(object):
    """do-nothing: forward all data unchanged"""
    def rx(self, text):
        """text received from serial port"""
        return text

    def tx(self, text):
        """text to be sent to serial port"""
        return text

    def echo(self, text):
        """text to be sent but displayed on console"""
        return text


class CRLF(Transform):
    """ENTER sends CR+LF"""

    def tx(self, text):
        return text.replace('\n', '\r\n')


class CR(Transform):
    """ENTER sends CR"""

    def rx(self, text):
        return text.replace('\r', '\n')

    def tx(self, text):
        return text.replace('\n', '\r')


class LF(Transform):
    """ENTER sends LF"""


class NoTerminal(Transform):
    """remove typical terminal control codes from input"""

    REPLACEMENT_MAP = dict((x, 0x2400 + x) for x in range(32) if unichr(x) not in '\r\n\b\t')
    REPLACEMENT_MAP.update(
        {
            0x7F: 0x2421,  # DEL
            0x9B: 0x2425,  # CSI
        })

    def rx(self, text):
        return text.translate(self.REPLACEMENT_MAP)

    echo = rx


class NoControls(NoTerminal):
    """Remove all control codes, incl. CR+LF"""

    REPLACEMENT_MAP = dict((x, 0x2400 + x) for x in range(32))
    REPLACEMENT_MAP.update(
        {
            0x20: 0x2423,  # visual space
            0x7F: 0x2421,  # DEL
            0x9B: 0x2425,  # CSI
        })


class Printable(Transform):
    """Show decimal code for all non-ASCII characters and replace most control codes"""

    def rx(self, text):
        r = []
        for c in text:
            if ' ' <= c < '\x7f' or c in '\r\n\b\t':
                r.append(c)
            elif c < ' ':
                r.append(unichr(0x2400 + ord(c)))
            else:
                r.extend(unichr(0x2080 + ord(d) - 48) for d in '{:d}'.format(ord(c)))
                r.append(' ')
        return ''.join(r)

    echo = rx


class Colorize(Transform):
    """Apply different colors for received and echo"""

    def __init__(self):
        # XXX make it configurable, use colorama?
        self.input_color = '\x1b[37m'
        self.echo_color = '\x1b[31m'

    def rx(self, text):
        return self.input_color + text

    def echo(self, text):
        return self.echo_color + text


# other ideas:
# - add date/time for each newline
# - insert newline after: a) timeout b) packet end character

EOL_TRANSFORMATIONS = {
    'crlf': CRLF,
    'cr': CR,
    'lf': LF,
}

TRANSFORMATIONS = {
    'direct': Transform,    # no transformation
    'default': NoTerminal,
    'nocontrol': NoControls,
    'printable': Printable,
    'colorize': Colorize,
}


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

class Miniterm(object):
    """\
    Terminal application. Copy data from serial port to console and vice versa.
    Handle special keys from the console to show menu etc.
    """

    def __init__(self, serial_instance, echo=False, eol='crlf', filters=(), features=(), exit_key='Ctrl+]'):
        self.console = Console()
        self.terminal = SimpleTerminal(self.console)
        self.escape_decoder = EscapeDecoder(self.terminal)
        self.escape_encoder = EscapeEncoder()
        self.serial = serial_instance
        self.echo = echo
        self.input_encoding = 'UTF-8'
        self.output_encoding = 'UTF-8'
        self.eol = eol
        self.filters = filters
        self.update_transformations()
        self.exit_key = exit_key
        self.alive = None
        self._reader_alive = None
        self.receiver_thread = None
        self.rx_decoder = None
        self.tx_decoder = None
        self.hotkeys = {}
        self.hotkeys[self.exit_key] = self.handle_exit_key
        self._features = [f(self, **kwargs) for f, kwargs in features]

    def _start_reader(self):
        """Start reader thread"""
        self._reader_alive = True
        # start serial->console thread
        self.receiver_thread = threading.Thread(target=self.reader, name='rx')
        self.receiver_thread.daemon = True
        self.receiver_thread.start()

    def _stop_reader(self):
        """Stop reader thread only, wait for clean exit of thread"""
        self._reader_alive = False
        if hasattr(self.serial, 'cancel_read'):
            self.serial.cancel_read()
        self.receiver_thread.join()

    def start(self):
        """start worker threads"""
        self.alive = True
        self._start_reader()
        # enter console->serial loop
        self.transmitter_thread = threading.Thread(target=self.writer, name='tx')
        self.transmitter_thread.daemon = True
        self.transmitter_thread.start()
        self.console.setup()
        for f in self._features:
            f.start()

    def stop(self):
        """set flag to stop worker threads"""
        self.alive = False

    def join(self, transmit_only=False):
        """wait for worker threads to terminate"""
        self.transmitter_thread.join()
        if not transmit_only:
            if hasattr(self.serial, 'cancel_read'):
                self.serial.cancel_read()
            self.receiver_thread.join()

    def close(self):
        self.serial.close()

    def update_transformations(self):
        """take list of transformation classes and instantiate them for rx and tx"""
        transformations = [EOL_TRANSFORMATIONS[self.eol]] + [TRANSFORMATIONS[f]
                                                             for f in self.filters]
        self.tx_transformations = [t() for t in transformations]
        self.rx_transformations = list(reversed(self.tx_transformations))

    def set_rx_encoding(self, encoding, errors='replace'):
        """set encoding for received data"""
        self.input_encoding = encoding
        self.rx_decoder = codecs.getincrementaldecoder(encoding)(errors)

    def set_tx_encoding(self, encoding, errors='replace'):
        """set encoding for transmitted data"""
        self.output_encoding = encoding
        self.tx_encoder = codecs.getincrementalencoder(encoding)(errors)

    def reader(self):
        """loop and copy serial->console"""
        try:
            while self.alive and self._reader_alive:
                # read all that is there or wait for one byte
                data = self.serial.read(self.serial.in_waiting or 1)
                for byte in serial.iterbytes(data):
                    try:
                        self.escape_decoder.handle(byte)
                    except Exception as e:
                        traceback.print_exc()
                    #     text = self.rx_decoder.decode(data)
                    #     for transformation in self.rx_transformations:
                    #         text = transformation.rx(text)
                    #     self.console.write(text)
        except serial.SerialException:
            self.alive = False
            self.console.cancel()
            raise       # XXX handle instead of re-raise?

    def send_key(self, key_name):
        if len(key_name) > 1:
            key_name = self.escape_encoder.translate_named_key(key_name)
        text = key_name
        for transformation in self.tx_transformations:
            text = transformation.tx(text)
        self.serial.write(self.tx_encoder.encode(text))
        if self.echo:
            echo_text = key_name
            for transformation in self.tx_transformations:
                echo_text = transformation.echo(echo_text)
            self.console.write(echo_text)

    def handle_exit_key(self, key_name):
        self.stop()  # exit app

    def writer(self):
        """Loop and copy console->serial."""
        try:
            while self.alive:
                try:
                    key_name = self.console.getkey()
                except KeyboardInterrupt:
                    key_name = '\x03'
                if not self.alive:
                    break
                callback = self.hotkeys.get(key_name, self.send_key)
                callback(key_name)
        except:
            self.alive = False
            raise


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# default args can be used to override when calling main() from an other script
# e.g to create a miniterm-my-device.py
def main(default_port=None, default_baudrate=9600, default_rts=None, default_dtr=None, serial_instance=None):
    """Command line tool, entry point"""

    import argparse

    MODIFIERS = ['Ctrl', 'Shift', 'Alt']
    USEFUL_KEYS = [
        'Esc', 'Tab', 'Insert', 'Delete',
        'F1', 'F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9', 'F10', 'F11', 'F12'
    ] + list('ABCDEFGHJKLMNOPQRSTXYZ\\]^_')  # keys with alternate names removed

    def check_key_name(key_name):
        parts = key_name.split('+')
        if len(parts) < 1:
            raise ValueError('key name missing')
        if parts.pop() not in USEFUL_KEYS:
            raise ValueError('invalid key name')
        for part in parts:
            if part not in MODIFIERS:
                raise ValueError('{!r} is not a valid modifier ({})'.format(part, MODIFIERS))
        return key_name

    parser = argparse.ArgumentParser(description="pySerial-terminal")

    parser.add_argument(
        "port",
        nargs='?',
        help="serial port name ('-' to show port list)",
        default=default_port)

    parser.add_argument(
        "baudrate",
        nargs='?',
        type=int,
        help="set baud rate, default: %(default)s",
        default=default_baudrate)

    group = parser.add_argument_group("port settings")

    group.add_argument(
        "--parity",
        choices=['N', 'E', 'O', 'S', 'M'],
        type=lambda c: c.upper(),
        help="set parity, one of {N E O S M}, default: N",
        default='N')

    group.add_argument(
        "--rtscts",
        action="store_true",
        help="enable RTS/CTS flow control (default off)",
        default=False)

    group.add_argument(
        "--xonxoff",
        action="store_true",
        help="enable software flow control (default off)",
        default=False)

    group.add_argument(
        "--rts",
        type=int,
        help="set initial RTS line state (possible values: 0, 1)",
        default=default_rts)

    group.add_argument(
        "--dtr",
        type=int,
        help="set initial DTR line state (possible values: 0, 1)",
        default=default_dtr)

    group.add_argument(
        "--ask",
        action="store_true",
        help="ask again for port when open fails",
        default=False)

    group = parser.add_argument_group("data handling")

    group.add_argument(
        "-e", "--echo",
        action="store_true",
        help="enable local echo (default off)",
        default=False)

    group.add_argument(
        "--encoding",
        metavar="CODEC",
        help="set the encoding for the serial port (e.g. hexlify, Latin1, UTF-8), default: %(default)s",
        default='UTF-8')

    group.add_argument(
        "-f", "--filter",
        action="append",
        metavar="NAME",
        help="add text transformation",
        default=[])

    group.add_argument(
        "--eol",
        choices=['CR', 'LF', 'CRLF'],
        type=lambda c: c.upper(),
        help="end of line mode",
        default='CRLF')

    group = parser.add_argument_group("hotkeys")

    group.add_argument(
        "--exit-key",
        type=check_key_name,
        metavar='KEY',
        help="Key that is used to exit the application, default: %(default)s",
        default='Ctrl+]')

    group.add_argument(
        "--menu-key",
        type=check_key_name,
        metavar='KEY',
        help="Key that is used to control miniterm (menu), default: %(default)s",
        default='Ctrl+T')

    group = parser.add_argument_group("diagnostics")

    group.add_argument(
        "--develop",
        action="store_true",
        help="show Python traceback on error",
        default=False)

    args = parser.parse_args()

    if args.menu_key == args.exit_key:
        parser.error('--exit-key can not be the same as --menu-key')

    if args.filter:
        if 'help' in args.filter:
            sys.stderr.write('Available filters:\n')
            sys.stderr.write('\n'.join(
                '{:<10} = {.__doc__}'.format(k, v)
                for k, v in sorted(TRANSFORMATIONS.items())))
            sys.stderr.write('\n')
            sys.exit(1)
        filters = args.filter
    else:
        filters = ['default']

    miniterm = Miniterm(
        None,
        echo=args.echo,
        eol=args.eol.lower(),
        filters=filters,
        features=[
            (startup_message.StartupMessage, {}),
            (menu.Menu, {'hot_key': args.menu_key}),
        ],
        exit_key=args.exit_key)

    while serial_instance is None:
        # no port given on command line -> ask user now
        if args.port is None or args.port == '-':
            try:
                args.port = ask_for_port.AskForPort(miniterm).ask_for_port()
            except KeyboardInterrupt:
                miniterm.console.write('\n')
                parser.error('user aborted and port is not given')
            else:
                if not args.port:
                    parser.error('port is not given')
        try:
            serial_instance = serial.serial_for_url(
                args.port,
                args.baudrate,
                parity=args.parity,
                rtscts=args.rtscts,
                xonxoff=args.xonxoff,
                do_not_open=True)

            if args.dtr is not None:
                miniterm.console.write('--- forcing DTR {}\n'.format('active' if args.dtr else 'inactive'))
                serial_instance.dtr = args.dtr
            if args.rts is not None:
                miniterm.console.write('--- forcing RTS {}\n'.format('active' if args.rts else 'inactive'))
                serial_instance.rts = args.rts

            serial_instance.open()
        except serial.SerialException as e:
            serial_instance = None
            miniterm.console.write('could not open port {}: {}\n'.format(repr(args.port), e))
            if args.develop:
                raise
            if not args.ask:
                sys.exit(1)
            else:
                args.port = '-'
        else:
            break

    if not hasattr(serial_instance, 'cancel_read'):
        # enable timeout for alive flag polling if cancel_read is not available
        serial_instance.timeout = 1

    miniterm.serial = serial_instance
    miniterm.set_rx_encoding(args.encoding)
    miniterm.set_tx_encoding(args.encoding)

    miniterm.start()
    try:
        miniterm.join(True)
    except KeyboardInterrupt:
        pass
    miniterm.console.write("\r\n--- exit ---\r\n")
    miniterm.join()
    miniterm.close()


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
if __name__ == '__main__':
    main()
