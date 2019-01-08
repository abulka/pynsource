import sys

print(repr(file(sys.argv[1], 'rb').read()[-500:]))
