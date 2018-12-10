=================
pySerial-Terminal
=================

A more capable(*), modular terminal (* than pySerial's miniterm)

Currently a work in progress.


Misc
====
There are some layers and indirections. The aim is to be able to implement
different I/O devices without re-implementing the escape decoder logic each
time.

console

- read keys (return key names)
- output operations using API (query/move cursor, erase parts)
- backends: windows, [posix, GUIs]

terminal

- escape_decoder: decode escape sequences and call methods on emulation object
- providing constants

emulation

- mapping escape_decoder calls to console
- simple version decoding colors and movements, not supporting some of the features
- [aiming for] nearly full VT220 (e.g. no printing support)


::

    ┏━━━━━━━━━━━━━━┓    ┏━━━━━━━━━━━━━━━━┓    ┏━━━━━━━━━━━┓    ┏━━━━━━━━━┓
    ┃ input stream ┃───>┃ escape_decoder ┃───>┃ emulation ┃───>┃ console ┃
    ┗━━━━━━━━━━━━━━┛    ┗━━━━━━━━━━━━━━━━┛    ┗━━━━━━━━━━━┛    ┗━━━━━━━━━┛
    ┏━━━━━━━━━┓    ┏━━━━━━━━━━━┓    ┏━━━━━━━━━━┓    ┏━━━━━━━━━━━━━━━┓
    ┃ console ┃───>┃ emulation ┃───>┃ terminal ┃───>┃ output stream ┃
    ┗━━━━━━━━━┛    ┗━━━━━━━━━━━┛    ┗━━━━━━━━━━┛    ┗━━━━━━━━━━━━━━━┛
