#!/usr/bin/env python
#
# Terminal emulation with some basic color and cursor movement.
#
# This file is part of pySerial-terminal. https://github.com/pyserial/pyserial-terminal
# (C) 2018 Chris Liechti <cliechti@gmx.net>
#
# SPDX-License-Identifier:    BSD-3-Clause

import codecs


class SimpleTerminal:
    def __init__(self, console):
        self.console = console
        self.decoder = codecs.getincrementaldecoder('utf-8')('replace')

    def select_graphic_rendition(self, colorcodes):
        if not colorcodes:
            colorcodes = [0]
        self.console.set_ansi_color(colorcodes)

    def carriage_return(self):
        x, y, width, height = self.console.get_position_and_size()
        self.console.set_cursor_position(0, y)
        # self.console.write_bytes(b'\r')

    def line_feed(self):
        x, y, width, height = self.console.get_position_and_size()
        self.console.set_cursor_position(x, y + 1)
        # self.console.write_bytes(b'\n')

    def backspace(self):
        # self.cursor_backward(1)
        x, y, width, height = self.console.get_position_and_size()
        self.console.erase(x - 1, y, 1, 1, False)
        self.console.set_cursor_position(x - 1, y)
        # self.console.write_bytes(b'\b')

    def bell(self):
        self.console.write_bytes(b'\g')

    def horizontal_tab(self):
        self.console.write_bytes(b'\t')

    # def enquiry(self):
    # def vertical_tabulation(self):
    # def form_feed(self):
    # def shift_out(self):
    # def shift_in(self):
    # def device_control_1(self):
    # def device_control_2(self):
    # def device_control_3(self):
    # def device_control_4(self):
    # def cancel(self):
    # def substitute(self):
    # def delete(self):
    # def index(self):
    # def next_line(self):
    # def horizontal_tab_set(self):
    # def reverse_index(self):
    # def single_shift_G2(self):
    # def single_shift_G3(self):
    # def device_control_string(self):
    # def string_terminator(self):
    # def index(self):
    # def next_line(self):
    # def horizontal_tab_set(self):
    # def reverse_index(self):
    # def single_shift_G2(self):
    # def single_shift_G3(self):
    # def device_control_string(self):
    # def string_terminator(self):
    # def operating_system_command(self):
    # def application_program_command(self):
    # def privacy_message(self):
    # def keypad_as_application(self):
    # def keypad_as_numeric(self):
    # def save_cursor(self):
    # def restore_cursor(self):
    # def convert_c1_codes(self, flag):
    # def handle_flag(self, flag_index, is_extra, value):

    def cursor_up(self, count):
        if count == 0:
            count = 1
        x, y, width, height = self.console.get_position_and_size()
        self.console.set_cursor_position(x, max(0, y - count))

    def cursor_down(self, count):
        if count == 0:
            count = 1
        x, y, width, height = self.console.get_position_and_size()
        self.console.set_cursor_position(x, min(height - 1, y + count))

    def cursor_forward(self, count):
        if count == 0:
            count = 1
        x, y, width, height = self.console.get_position_and_size()
        self.console.set_cursor_position(min(width - 1, x + count), y)

    def cursor_backward(self, count):
        if count == 0:
            count = 1
        x, y, width, height = self.console.get_position_and_size()
        self.console.set_cursor_position(max(0, x - count), y)

    def cursor_position(self, column, line):
        y = (line - 1) if line > 0 else 0
        x = (column - 1) if column > 0 else 0
        self.console.set_cursor_position(x, y)

    # def insert_line(self, mode):
    # def delete_line(self, mode):
    # def insert_character(self, mode):
    # def delete_character(self, mode):
    # def erase_display(self, mode, selective=False):
    def erase_in_line(self, mode, selective=False):
        x, y, width, height = self.console.get_position_and_size()
        if mode == 0:  # erase to end of line
            self.console.erase(x, y, width - x, 1, selective)
        elif mode == 1:  # erase to start of line
            self.console.erase(0, y, x, 1, selective)
        elif mode == 2:  # erase the complete line
            self.console.erase(0, y, width, 1, selective)
        else:
            raise ValueError('bad mode selection: {}'.format(mode))
        self.console.set_cursor_position(x, y)

    # def erase_character(self, mode, selective=False):
    # def clear_tabulation(self, mode):
    # def set_scroll_region_margins(self, a, b):

    def write(self, byte):
        data = self.decoder.decode(byte)
        self.console.write(data)
