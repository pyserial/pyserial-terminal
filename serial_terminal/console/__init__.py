#!/usr/bin/env python
#
# This is a wrapper module for different platform implementations
#
# This file is part of pySerial. https://github.com/pyserial/pyserial
# (C) 2001-2017 Chris Liechti <cliechti@gmx.net>
#
# SPDX-License-Identifier:    BSD-3-Clause

from __future__ import absolute_import

import os

if os.name == 'nt':  # noqa
    from .windows import Console
elif os.name == 'posix':
    from .posix import Console
else:
    raise NotImplementedError(
        'Sorry no implementation for your platform ({}) available.'.format(os.name))
