import sys

for fg in range(30, 38):
    sys.stdout.write('\x1b[{0}m {0} \x1b[0m'.format(fg))
for bg in range(40, 48):
    sys.stdout.write('\x1b[{0}m {0} \x1b[0m'.format(bg))

sys.stdout.write('\n')

