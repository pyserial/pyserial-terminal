#!/usr/bin/env python3
#
# Python 3+ only tkinter terminal widget.
#
# This file is part of pySerial-terminal. https://github.com/pyserial/pyserial-terminal
# (C) 2018 Chris Liechti <cliechti@gmx.net>
#
# SPDX-License-Identifier:    BSD-3-Clause

import queue
import tkinter as tk
from tkinter import scrolledtext

# from .base import ConsoleBase
from ..terminal import constants

keymap = {
    '<F1>': 'F1',
    '<F2>': 'F2',
    '<F3>': 'F3',
    '<F4>': 'F4',
    '<F5>': 'F5',
    '<F6>': 'F6',
    '<F7>': 'F7',
    '<F8>': 'F8',
    '<F9>': 'F9',
    '<F10>': 'F10',
    '<F11>': 'F11',
    '<F12>': 'F12',
    '<Shift-F1>': 'Shift+F1',
    '<Shift-F2>': 'Shift+F2',
    '<Shift-F3>': 'Shift+F3',
    '<Shift-F4>': 'Shift+F4',
    '<Shift-F5>': 'Shift+F5',
    '<Shift-F6>': 'Shift+F6',
    '<Shift-F7>': 'Shift+F7',
    '<Shift-F8>': 'Shift+F8',
    '<Shift-F9>': 'Shift+F9',
    '<Shift-F10>': 'Shift+F0',
    '<Shift-F11>': 'Shift+F1',
    '<Shift-F12>': 'Shift+F2',
    '<Control-F1>': 'Ctrl+F1',
    '<Control-F2>': 'Ctrl+F2',
    '<Control-F3>': 'Ctrl+F3',
    '<Control-F4>': 'Ctrl+F4',
    '<Control-F5>': 'Ctrl+F5',
    '<Control-F6>': 'Ctrl+F6',
    '<Control-F7>': 'Ctrl+F7',
    '<Control-F8>': 'Ctrl+F8',
    '<Control-F9>': 'Ctrl+F9',
    '<Control-F10>': 'Ctrl+F10',
    '<Control-F11>': 'Ctrl+F11',
    '<Control-F12>': 'Ctrl+F12',
    '<Shift-Control-F1>': 'Shift+Ctrl+F1',
    '<Shift-Control-F2>': 'Shift+Ctrl+F2',
    '<Shift-Control-F3>': 'Shift+Ctrl+F3',
    '<Shift-Control-F4>': 'Shift+Ctrl+F4',
    '<Shift-Control-F5>': 'Shift+Ctrl+F5',
    '<Shift-Control-F6>': 'Shift+Ctrl+F6',
    '<Shift-Control-F7>': 'Shift+Ctrl+F7',
    '<Shift-Control-F8>': 'Shift+Ctrl+F8',
    '<Shift-Control-F9>': 'Shift+Ctrl+F9',
    '<Shift-Control-F10>': 'Shift+Ctrl+F10',
    '<Up>': 'Up',
    '<Down>': 'Down',
    '<Left>': 'Left',
    '<Right>': 'Right',
    '<Home>': 'Home',
    '<End>': 'End',
    '<Insert>': 'Insert',
    '<Delete>': 'Delete',
    '<Prior>': 'Page Up',
    '<Next>': 'Page Down',
}


class Console(scrolledtext.ScrolledText):
    def __init__(self, *args, **kwargs):
        # super().__init__(width=80, height=25)
        super().__init__(width=132, height=52)
        # self.insert(tk.INSERT, '\n'.join(' ' * 132 for line in range(52)))
        # self.mark_set(tk.INSERT, 1.0)
        self._font = ("DejaVu Sans Mono", 10)
        self._bold_font = ("DejaVu Sans Mono", 10, "bold")
        self.config(background='#000000', foreground='#bbbbbb', insertbackground='#99ff99', font=self._font)
        self.tag_config('30', foreground='#000000')
        self.tag_config('31', foreground='#bb0000')
        self.tag_config('32', foreground='#00bb00')
        self.tag_config('33', foreground='#bbbb00')
        self.tag_config('34', foreground='#0000bb')
        self.tag_config('35', foreground='#bb00bb')
        self.tag_config('36', foreground='#00bbbb')
        self.tag_config('37', foreground='#bbbbbb')
        self.tag_config('40', background='#000000')
        self.tag_config('41', background='#bb0000')
        self.tag_config('42', background='#00bb00')
        self.tag_config('43', background='#bbbb00')
        self.tag_config('44', background='#0000bb')
        self.tag_config('45', background='#bb00bb')
        self.tag_config('46', background='#00bbbb')
        self.tag_config('47', background='#bbbbbb')
        self.tag_config('90', foreground='#555555')
        self.tag_config('91', foreground='#ff5555')
        self.tag_config('92', foreground='#55ff55')
        self.tag_config('93', foreground='#ffff55')
        self.tag_config('94', foreground='#5555ff')
        self.tag_config('95', foreground='#ff55ff')
        self.tag_config('96', foreground='#55ffff')
        self.tag_config('97', foreground='#ffffff')
        self.tag_config('100', background='#555555')
        self.tag_config('101', background='#ff5555')
        self.tag_config('102', background='#55ff55')
        self.tag_config('103', background='#ffff55')
        self.tag_config('104', background='#5555ff')
        self.tag_config('105', background='#ff55ff')
        self.tag_config('106', background='#55ffff')
        self.tag_config('107', background='#ffffff')
        # self.tag_config('1', font=("Courier", 10, "bold"))
        # self.tag_config('0', font=("Courier", 10))
        self.tag_config('1', font=self._bold_font)
        self.tag_config('0', font=self._font)
        self._fg = ''
        self._bg = ''
        self._bold = ''
        for key, key_name in keymap.items():
            self.bind(key, lambda event, key_name=key_name: self._send_key(key_name))
        self.bind('<Key>', lambda event: self._send_key(event.char))
        # avoid selection and direct cursor positioning
        self.bind('<Button-1>', lambda event: 'break')
        self.bind('<B1-Motion>', lambda event: 'break')
        self._input_queue = queue.Queue()

    def setup(self):
        pass

    def _send_key(self, key):
        self._input_queue.put(key)
        return "break"  # stop event propagation

    def getkey(self):
        """read (named keys) from console"""
        return self._input_queue.get()

    def cancel(self):
        self._input_queue.put(None)

    def write_bytes(self, text):
        self.insert(tk.INSERT, text, (self._fg, self._bg, self._bold))

    def flush(self):
        pass

    def write(self, text):
        """write text"""
        contents = self.get(tk.INSERT, f'insert+{len(text)}c')
        if contents:
            self.delete(tk.INSERT, f'insert+{len(contents)}c')
        self.insert(tk.INSERT, text, (self._fg, self._bg, self._bold))

    def set_ansi_color(self, colorcodes):
        """set color/intensity for next write(s)"""
        for colorcode in colorcodes:
            if colorcode == 0:
                self._fg = ''
                self._bg = ''
            if colorcode in constants.Foreground.__dict__.values():
                self._fg = colorcode
            if colorcode in constants.Background.__dict__.values():
                self._bg = colorcode
            if colorcode in (0, 1):
                self._bold = colorcode

    def get_position_and_size(self):
        """get cursor position (zero based) and window size"""
        index = self.index(tk.INSERT)
        y, x = [int(s) for s in index.split('.')]
        width = self.cget('width')
        height = self.cget('height')
        # print('getpos', x, y - 1, width, height)
        return x, y - 1, width, height

    def set_cursor_position(self, x, y):
        """set cursor position (zero based)"""
        # print('setpos', x, y)
        self.mark_set(tk.INSERT, f'{y + 1}.{x}')

    def move_or_scroll_down(self):
        """move cursor down, extend and scroll if needed"""
        y, x = [int(s) for s in self.index(tk.INSERT).split('.')]
        end_y, end_x = [int(s) for s in self.index(tk.END).split('.')]
        if y + 1 >= end_y:
            self.insert(tk.END, '\n\n' + ' ' * x)
        self.mark_set(tk.INSERT, f'{y + 1}.{x}')
        self.see(tk.INSERT)

    def move_or_scroll_up(self):
        """move cursor up, extend and scroll if needed"""
        y, x = [int(s) for s in self.index(tk.INSERT).split('.')]
        if y - 1 <= 0:
            self.insert(1.0, '\n\n' + ' ' * x)
        self.mark_set(tk.INSERT, f'{y - 1}.{x}')
        self.see(tk.INSERT)

    def erase(self, x, y, width, height, selective=False):
        """erase rectangular area"""
        # print('erase', x, y, width, height, selective)
        for _y in range(y + 1, y + height + 1):
            self.delete(f'{_y}.{x}', f'{_y}.{x + width}')
            self.insert(f'{_y}.{x}', ' ' * width)
        #     if not selective:
        #         attrs
