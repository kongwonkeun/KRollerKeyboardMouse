#
#
#

import sys
from pynput.mouse import Controller, Listener

G_mouse = Controller()

#================================
#
#
def click(btn, count):
    G_mouse.click(btn, count)
    return

def move(dx, dy):
    G_mouse.move(dx, dy)
    return

def position():
    p = G_mouse.position
    print(f"mouse position = {p}")
    return p

def set_position(x, y):
    G_mouse.position = (x, y)
    return

def press(btn):
    G_mouse.press(btn)
    return

def release(btn):
    G_mouse.release(btn)
    return

def scroll(dx, dy):
    G_mouse.scroll(dx, dy)
    return

#================================
#
#
def monitor():
    # listener is a threading.Thread
    # .stop
    # .StopException or
    # return False from a callback to stop listener
    with Listener(on_move=on_move, on_click=on_click, on_scroll=on_scroll) as listener:
        listener.join()
    return

def on_move(x, y):
    print(f"mouse moved to ({x},{y})")
    return

def on_click(x, y, button, pressed):
    if  pressed:
        print(f"mouse pressed at ({x},{y})")
    else:
        print(f"mouse released at ({x},{y})")
        return False # stop listener
    return

def on_scroll(x, y, dx, dy):
    if  dy < 0:
        print(f"mouse scroll up at ({x},{y})")
    else:
        print(f"mouse scroll down at ({x},{y})")
    return

#
# eof
#
