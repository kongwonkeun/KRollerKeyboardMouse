#
#
#

import sys
import ctypes
import msvcrt
import time

import zMouse
import zKey
import zBt

#================================
#
#
def connectBt(bt: zBt.Bt):

    print("type 'q' to quit the bluetooth connection and receiving test")
    bt.connect()

    while True:
        time.sleep(1)
        if  msvcrt.kbhit():
            c = msvcrt.getch()
            if  c == b'q':
                bt.stop()
                break
    time.sleep(1)
    return

#================================
#
#
def typeKey():

    print("type 'q' to quit the key typing test")

    f = True
    while (f):
        zKey.type('A')
        time.sleep(1)
        if  msvcrt.kbhit():
            c = msvcrt.getch()
            if  c == b'q':
                f = False
    return

#================================
#
#
def moveMouse():

    s = ctypes.windll.user32
    w = s.GetSystemMetrics(0) # display width
    h = s.GetSystemMetrics(1) # display height
    w -= 10
    h -= 10

    print("type 'q' to quit tte mouse pointer moving test")

    f = True
    while (f):
        p = zMouse.position()
        zMouse.move(10, 10)
        if  p[0] > w or p[1] > h:
            zMouse.set_position(10, 10)
        time.sleep(1)
        if  msvcrt.kbhit():
            c = msvcrt.getch()
            if  c == b'q':
                f = False
    return

#
# eof
#
