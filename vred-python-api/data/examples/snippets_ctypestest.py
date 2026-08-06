# ctypestest
# source: ctypestest.html

# © 2026 Autodesk, Inc. All rights reserved.

from ctypes import *
libc = cdll.msvcrt 
print(libc)
printf = libc.printf
printf(b"Hello, %s\n", b"World!")
