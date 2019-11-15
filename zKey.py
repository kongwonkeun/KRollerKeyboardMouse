#
#
#

import sys
from pynput.keyboard import Key, Controller, Listener

G_key = Controller()

#================================
#
#
def type(key):
    G_key.press(key)
    G_key.release(key)
    return

def press(key):
    G_key.press(key)
    return

def release(key):
    G_key.release(key)
    return

#================================
#
#
def monitor():
    # listener is a threading.Thread
    # .stop
    # .StopException or
    # return False from a callback to stop listener
    with Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()
    return

def on_press(key):
    print(f"{key} pressed")
    return

def on_release(key):
    print(f"{key} released")
    if  key == Key.esc:
        return False # stop listener
    return

#
# eof
#
