#! /usr/bin/env python3
import sys

def main():
    sys.stdout.write('     ')
    for background in [''] + ['{}'.format(b) for b in range(40, 48)] + ['{}'.format(b) for b in range(100, 108)]:
        sys.stdout.write('{:>4}m '.format(background))
    sys.stdout.write('\n')
    for foreground in [''] + ['{}'.format(f) for f in range(30, 38)] + ['{}'.format(f) for f in range(90, 98)]:
        for intensity in ('', '1'):
            sys.stdout.write('{:>4}m '.format(';'.join(c for c in (intensity, foreground) if c)))
            for background in [''] + ['{}'.format(b) for b in range(40, 48)] + ['{}'.format(b) for b in range(100, 108)]:
                color = ';'.join(c for c in (intensity, foreground, background) if c)
                sys.stdout.write('\x1b[{}m ABC \x1b[0m '.format(color))
            sys.stdout.write('\n')
    sys.stdout.write('\x1b[0m')


if __name__ == '__main__':
    main()
