
#!/usr/bin/env python
# encoding: utf-8
#
# Generate escape sequences.
#
# This file is part of pySerial-terminal. https://github.com/pyserial/pyserial-terminal
# (C) 2018 Chris Liechti <cliechti@gmx.net>
#
# SPDX-License-Identifier:    BSD-3-Clause


class EscapeEncoder:
    def __init__(self, output_stream=None):
        self.output_stream = output_stream
        self.keymap = {
            'Ctrl+Space': '\x00',
            'Ctrl+A': '\x01',
            'Ctrl+B': '\x02',
            'Ctrl+C': '\x03',
            'Ctrl+D': '\x04',
            'Ctrl+E': '\x05',
            'Ctrl+F': '\x06',
            'Ctrl+G': '\x07',
            'Ctrl+H': '\x08',
            'Ctrl+I': '\x09',
            'Ctrl+J': '\x0a',
            'Ctrl+K': '\x0b',
            'Ctrl+L': '\x0c',
            'Ctrl+M': '\x0d',
            'Ctrl+N': '\x0e',
            'Ctrl+O': '\x0f',
            'Ctrl+P': '\x10',
            'Ctrl+Q': '\x11',
            'Ctrl+R': '\x12',
            'Ctrl+S': '\x13',
            'Ctrl+T': '\x14',
            'Ctrl+U': '\x15',
            'Ctrl+V': '\x16',
            'Ctrl+W': '\x17',
            'Ctrl+X': '\x18',
            'Ctrl+Y': '\x19',
            'Ctrl+Z': '\x1a',
            'Ctrl+[': '\x1b',
            'Ctrl+\\': '\x1c',
            'Ctrl+]': '\x1d',
            'Ctrl+^': '\x1e',
            'Ctrl+_': '\x1f',
            'Tab': '\x09',
            'Esc': '\x1d',
            'PF1': '\x1bOP',
            'PF2': '\x1bOQ',
            'PF3': '\x1bOR',
            'PF4': '\x1bOS',
            'F1': '\x1b[11~',
            'F2': '\x1b[12~',
            'F3': '\x1b[13~',
            'F4': '\x1b[14~',
            'F5': '\x1b[15~',
            'F6': '\x1b[17~',
            'F7': '\x1b[18~',
            'F8': '\x1b[19~',
            'F9': '\x1b[20~',
            'F10': '\x1b[21~',
            'F11': '\x1b[23~',
            'F12': '\x1b[24~',
            'F13': '\x1b[25~',
            'F14': '\x1b[26~',
            'F15': '\x1b[28~',
            'F16': '\x1b[29~',
            'F17': '\x1b[31~',
            'F18': '\x1b[32~',
            'F19': '\x1b[33~',
            'F20': '\x1b[34~',
            'Up': '\x1b[A',
            'Down': '\x1b[B',
            'Left': '\x1b[D',
            'Right': '\x1b[C',
            'Home': '\x1b[H',
            'End': '\x1b[F',
            'Find': '\x1b[1~',
            'Insert': '\x1b[2~',
            'Delete': '\x1b[3~',
            'Select': '\x1b[4~',
            'Page Up': '\x1b[5~',
            'Page Down': '\x1b[6~',
            'Num Lock': '\x1bOP',
            'KP_Divide': '\x1bOQ',
            'KP_Multiply': '\x1bOR',
            'KP_Minus': '\x1bOS',
            'Caps Lock': '\x1bOm',
            'KP_Plus': '\x1bOl',
            'KP_Dot': '\x1bOn',
            'KP_Enter': '\x1bOM',
            'KP_0': '\x1bOp',
            'KP_1': '\x1bOq',
            'KP_2': '\x1bOr',
            'KP_3': '\x1bOs',
            'KP_4': '\x1bOt',
            'KP_5': '\x1bOu',
            'KP_6': '\x1bOv',
            'KP_7': '\x1bOw',
            'KP_8': '\x1bOx',
            'KP_9': '\x1bOy',
        }

    def translate_named_key(self, key_name):
        return self.keymap[key_name]

    def send_named_key(self, key_name):
        self.output_stream.write(self.translate_named_key(key_name))
