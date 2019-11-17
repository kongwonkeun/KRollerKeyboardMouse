#
#
#

import sys
import ctypes
import msvcrt
import time

import zBt
import zTest
import zPipe
import zKey
import zMouse

G_bt = zBt.Bt()

#================================
#
#
if  __name__ == '__main__':

    print("hello world")

    #zMouse.monitor()
    #zKey.monitor()
    #zTest.connectBt(G_bt)
    #zTest.typeKey()
    #zTest.moveMouse()
    #sys.exit()

    if  len(sys.argv) < 2:
        print("usage: kroller s or fb or f or b")

    elif sys.argv[1] == 's':
        G_bt.connect()

        if  not zBt.G_connected:
            print("kroller not found or connection failed")
            sys.exit()

        zPipe.launcher()
        G_bt.stop()

    elif sys.argv[1] == 'fb':
        zPipe.foobar_client()

    elif sys.argv[1] == 'f':
        zPipe.foo_client()

    elif sys.argv[1] == 'b':
        zPipe.bar_client()

    else:
        print("usage: kroller s or fb or f or b")

    sys.exit()

#
# eof
#
