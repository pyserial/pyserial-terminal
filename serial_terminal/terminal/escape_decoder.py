#!/usr/bin/env python
# encoding: utf-8
#
# Parse escape sequences and map them to calls to an emulator.
#
# This file is part of pySerial-terminal. https://github.com/pyserial/pyserial-terminal
# (C) 2018 Chris Liechti <cliechti@gmx.net>
#
# SPDX-License-Identifier:    BSD-3-Clause

# C0 control codes
NUL = b'\0'
SOH = b'\x01'
STX = b'\x02'
ETX = b'\x03'
EOT = b'\x04'
ENQ = b'\x05'
ACK = b'\x06'
BEL = b'\x07'
BS = b'\x08'
HT = b'\x09'
LF = b'\x0A'
VT = b'\x0B'
FF = b'\x0C'
CR = b'\x0D'
SO = b'\x0E'
SI = b'\x0F'
DLE = b'\x10'
DC1 = b'\x11'
DC2 = b'\x12'
DC3 = b'\x13'
DC4 = b'\x14'
NAK = b'\x15'
SYN = b'\x16'
ETB = b'\x17'
CAN = b'\x18'
EM = b'\x19'
SUB = b'\x1A'
ESC = b'\x1B'
FS = b'\x1C'
GS = b'\x1D'
RS = b'\x1E'
US = b'\x1F'
DEL = b'\x7F'

# C1 control codes
PAD = b'\x80'
HOP = b'\x81'
BPH = b'\x82'
NBH = b'\x83'
IND = b'\x84'
NEL = b'\x85'
SSA = b'\x86'
ESA = b'\x87'
HTS = b'\x88'
HTJ = b'\x89'
VTS = b'\x8A'
PLD = b'\x8B'
PLU = b'\x8C'
RI = b'\x8D'
SS2 = b'\x8E'
SS3 = b'\x8F'
DCS = b'\x90'
PU1 = b'\x91'
PU2 = b'\x92'
STS = b'\x93'
CCH = b'\x94'
MW = b'\x95'
SPA = b'\x96'
EPA = b'\x97'
SOS = b'\x98'
SGCI = b'\x99'
SCI = b'\x9A'
CSI = b'\x9B'
ST = b'\x9C'
OSC = b'\x9D'
PM = b'\x9E'
APC = b'\x9F'


class EscapeDecoder:
    def __init__(self, terminal_code_handler):
        self.terminal_code_handler = terminal_code_handler
        self._d_parameter = [0] * 3
        self._d_parameter_index = 0
        self._extra_flag = False
        self._value = None
        self._handler = self.handle_c0
        self.eightbit_controls = False

    def _reset_parameters(self):
        self._d_parameter[0] = 0
        self._d_parameter_index = 0
        self._extra_flag = False

    def handle(self, character):
        # h = self._handler
        self._handler(character)
        # print(h.__name__, repr(character), self._handler.__name__)   # XXX

    def handle_c0(self, character):
        if character == NUL:
            pass
        elif character == ENQ:
            self.terminal_code_handler.enquiry()
        elif character == BEL:
            self.terminal_code_handler.bell()
        elif character == BS:
            self.terminal_code_handler.backspace()
        elif character == HT:
            self.terminal_code_handler.horizontal_tab()
        elif character == LF:
            self.terminal_code_handler.line_feed()
        elif character == VT:
            self.terminal_code_handler.vertical_tabulation()
        elif character == FF:
            self.terminal_code_handler.form_feed()
        elif character == CR:
            self.terminal_code_handler.carriage_return()
        elif character == SO:
            self.terminal_code_handler.shift_out()
        elif character == SI:
            self.terminal_code_handler.shift_in()
        elif character == DC1:
            self.terminal_code_handler.device_control_1()
        elif character == DC2:
            self.terminal_code_handler.device_control_2()
        elif character == DC3:
            self.terminal_code_handler.device_control_3()
        elif character == DC4:
            self.terminal_code_handler.device_control_4()
        elif character == CAN:
            self.terminal_code_handler.cancel()
        elif character == SUB:
            self.terminal_code_handler.substitute()
        elif character == ESC:
            #~ self.terminal_code_handler.escape()
            self._reset_parameters()
            self._handler = self.handle_esc
        elif character == DEL:
            self.terminal_code_handler.delete()
        elif self.eightbit_controls:
            if character == IND:
                self.terminal_code_handler.index()
            elif character == NEL:
                self.terminal_code_handler.next_line()
            elif character == HTS:
                self.terminal_code_handler.horizontal_tab_set()
            elif character == RI:
                self.terminal_code_handler.reverse_index()
            elif character == SS2:
                self.terminal_code_handler.single_shift_G2()
            elif character == SS3:
                self.terminal_code_handler.single_shift_G3()
            elif character == DCS:
                self.terminal_code_handler.device_control_string()
            elif character == CSI:
                self._reset_parameters()
                self._handler = self.handle_csi
            elif character == ST:
                self.terminal_code_handler.string_terminator()
            else:
                self.terminal_code_handler.write(character)
        else:
            self.terminal_code_handler.write(character)

    #~ def self.handle_vt52_line(self, character):
        #~ self._value = ord(character) - 32
        #~ self._handler = self.handle_vt52_column
#~ 
    #~ def handle_vt52_column(self, character):
        #~ self.terminal_code_handler.cursor_position(self._value, ord(character) - 32)
        #~ self._handler = self.handle_c0

    def handle_esc(self, character):
        self._handler = self.handle_c0
        if character == b'D':    # IND
            self.terminal_code_handler.index()
        elif character == b'E':  # NEL
            self.terminal_code_handler.next_line()
        elif character == b'H':  # HTS
            self.terminal_code_handler.horizontal_tab_set()
        elif character == b'M':  # RI
            self.terminal_code_handler.reverse_index()
        elif character == b'N':  # SS2
            self.terminal_code_handler.single_shift_G2()
        elif character == b'O':  # SS3
            self.terminal_code_handler.single_shift_G3()
        elif character == b'P':  # DCS
            self.terminal_code_handler.device_control_string()
        elif character == b'[':  # CSI
            self._handler = self.handle_csi
        elif character == b'\\':  # ST
            self.terminal_code_handler.string_terminator()
        elif character == b']':  # OSC
            self.terminal_code_handler.operating_system_command()
        elif character == b'_':  # APC
            self.terminal_code_handler.application_program_command()
        elif character == b'^':  # PM
            self.terminal_code_handler.privacy_message()
        #~ elif character == b'~':  # LS1R
        #~ elif character == b'n':  # LS2
        #~ elif character == b'}':  # LS2R
        #~ elif character == b'o':  # LS3
        #~ elif character == b'|':  # LS3R
        elif character == b' ':  # S7C1T / S8C1T  # XXX ignore in VT100/VT52 modes
            self._handler = self.handle_select_control_transmission
        elif character == b'#':  # line attributes
            self._handler = self.handle_line_attributes
        elif character in b'()*+':
            self._value = ord(character)
            self._handler = self.handle_character_set_selection
        elif character == b'=':
            self.terminal_code_handler.keypad_as_application()
        elif character == b'>':
            self.terminal_code_handler.keypad_as_numeric()
        elif character == b'7':
            self.terminal_code_handler.save_cursor()
        elif character == b'8':
            self.terminal_code_handler.restore_cursor()
        #~ elif character == b'A':
            #~ self.terminal_code_handler.cursor_up()
        #~ elif character == b'B':
            #~ self.terminal_code_handler.cursor_down()
        #~ elif character == b'C':
            #~ self.terminal_code_handler.cursor_forward()
        #~ elif character == b'D':
            #~ self.terminal_code_handler.cursor_backward()
        #~ elif character == b'F':
            #~ self.terminal_code_handler.graphics_mode(True)
        #~ elif character == b'G':
            #~ self.terminal_code_handler.graphics_mode(False)
        #~ elif character == b'H':
            #~ self.terminal_code_handler.cursor_position(0, 0)
        #~ elif character == b'I':
            #~ self.terminal_code_handler.reverse_line_feed()
        #~ elif character == b'J':
            #~ self.terminal_code_handler.erase_display(0)
        #~ elif character == b'K':
            #~ self.terminal_code_handler.erase_in_line(0)
        #~ elif character == b'Y':
            #~ self._handler = self.handle_vt52_line
        #~ elif character == b'Z':
            #~ self.terminal_code_handler.identify()
        #~ elif character == b'<':
            #~ self.terminal_code_handler.ansi_mode()
        #~ elif character == b']':
            #~ self.terminal_code_handler.print_screen()
        #~ elif character == b'V':
            #~ self.terminal_code_handler.print_cursor_line()
        # left out ' '/'_' autoprint and 'W'/'X' printer control mode
        elif character == ESC:
            self.terminal_code_handler.write(character)
            self._handler = self.handle_c0
        else:
            self._handler = self.handle_c0

    def handle_select_control_transmission(self, character):
        if character == b'F':
            self.terminal_code_handler.convert_c1_codes(True)
        elif character == b'G':
            self.terminal_code_handler.convert_c1_codes(False)
        self._handler = self.handle_c0

    def handle_line_attributes(self, character):
        # XXX
        self._handler = self.handle_c0

    def handle_character_set_selection(self, character):
        #~ self._value  # select group
        # XXX
        self._handler = self.handle_c0

    def handle_csi(self, character):
        if character == b'h':
            self._handler = self.handle_c0
            self.terminal_code_handler.handle_flag(self._d_parameter[0], self._extra_flag, True)
        elif character == b'l':
            self._handler = self.handle_c0
            self.terminal_code_handler.handle_flag(self._d_parameter[0], self._extra_flag, False)
        elif character == b'A':
            self._handler = self.handle_c0
            self.terminal_code_handler.cursor_up(self._d_parameter[0])
        elif character == b'B':
            self._handler = self.handle_c0
            self.terminal_code_handler.cursor_down(self._d_parameter[0])
        elif character == b'C':
            self._handler = self.handle_c0
            self.terminal_code_handler.cursor_forward(self._d_parameter[0])
        elif character == b'D':
            self._handler = self.handle_c0
            self.terminal_code_handler.cursor_backward(self._d_parameter[0])
        elif character == b'H':
            self._handler = self.handle_c0
            self.terminal_code_handler.cursor_position(self._d_parameter[0], self._d_parameter[1])
        elif character == b'L':  # IL
            self._handler = self.handle_c0
            self.terminal_code_handler.insert_line(self._d_parameter[0])
        elif character == b'M':  # DL
            self._handler = self.handle_c0
            self.terminal_code_handler.delete_line(self._d_parameter[0])
        elif character == b'@':  # ICH
            self._handler = self.handle_c0
            self.terminal_code_handler.insert_character(self._d_parameter[0])
        elif character == b'P':  # DCH
            self._handler = self.handle_c0
            self.terminal_code_handler.delete_character(self._d_parameter[0])
        elif character == b'X':  # ECH
            self._handler = self.handle_c0
            self.terminal_code_handler.erase_character(self._d_parameter[0])
        elif character == b'K':  # EL
            self._handler = self.handle_c0
            self.terminal_code_handler.erase_in_line(self._d_parameter[0], selective=self._extra_flag)
        elif character == b'J':  # ED
            self._handler = self.handle_c0
            self.terminal_code_handler.erase_display(self._d_parameter[0], selective=self._extra_flag)
        elif character == b'f':
            self._handler = self.handle_c0
            self.terminal_code_handler.cursor_position(self._d_parameter[0], self._d_parameter[1])
        elif character == b'g':
            self._handler = self.handle_c0
            self.terminal_code_handler.clear_tabulation(self._d_parameter[0])
        elif character == b'm':
            self.terminal_code_handler.select_graphic_rendition(self._d_parameter[:self._d_parameter_index + 1])
            self._handler = self.handle_c0
        elif character == b'r':  # DECSTBM
            self.terminal_code_handler.set_scroll_region_margins(self._d_parameter[0], self._d_parameter[1])
            self._handler = self.handle_c0
        #~ elif character == b'"':  # sel character attribs, followed by b'q'
        #~ elif character == b'i':  # printing
        elif character == b';':          # parameter separator
            if self._d_parameter_index < len(self._d_parameter):
                self._d_parameter_index += 1
                self._d_parameter[self._d_parameter_index] = 0
        elif character == b'?':          # ANSI private extensions marker
            self._extra_flag = True
        elif character in b'0123456789':  # parse individual parameter (numbers)
            self._d_parameter[self._d_parameter_index] *= 10
            self._d_parameter[self._d_parameter_index] += ord(character) - ord('0')

        # unknown CSI sequences are ignored
        else:
            self._handler = self.handle_c0
