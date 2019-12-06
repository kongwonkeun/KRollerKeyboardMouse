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
def help():

    print("usage:")
    print("> kroller s  --> kroller server for the pipes (foobar, foo)")
    print("> kroller sb --> krokker server for the pipes (foobar, foo, bar)")
    print("> krokker sr --> kroller server for the pipes (foobar, foo, RDTLauncherPipe)")
    print("> kroller fb --> kroller client for foobar (rx) pipe")
    print("> kroller f  --> kroller client for foo (rx) pipe")
    print("> kroller b  --> kroller client for bar (tx) pipe")
    print("> kroller r  --> kroller client for RDTLauncherPipe (tx) pipe")
    return

#================================
#
#
def connect():

    G_bt.connect()
    if  not zBt.G_connected:
        print("kroller not found or connection failed")
        sys.exit(zBt.BT_ERROR)
    return

#================================
#
#
def test():

    #zMouse.monitor()
    #zKey.monitor()
    #zTest.connectBt(G_bt)
    #zTest.typeKey()
    #zTest.moveMouse()
    #sys.exit()
    return

#================================
#
#
if  __name__ == '__main__':

    print("hello world")
    #test()

    if  len(sys.argv) < 2:
        help()

    elif sys.argv[1] == 's':
        connect()
        zPipe.launcher('s')

    elif sys.argv[1] == 'sb':
        connect()
        zPipe.launcher('sb')

    elif sys.argv[1] == 'sr':
        connect()
        zPipe.launcher('sr')

    elif sys.argv[1] == 'fb':
        zPipe.foobar_client()

    elif sys.argv[1] == 'f':
        zPipe.foo_client()

    elif sys.argv[1] == 'b':
        zPipe.bar_client()

    elif sys.argv[1] == 'r':
        zPipe.rdt_client()

    else:
        help()

    if  zBt.G_connected:
        G_bt.stop()

    sys.exit()

#
# eof
#
