#
#
#

import sys
import time
import win32api, win32pipe, win32file, pywintypes
import ctypes
import msvcrt
import threading

PIPE_FOO = r"\\.\pipe\foo"
PIPE_BAR = r"\\.\pipe\bar"
PIPE_BAZ = r"\\.\pipe\baz"
PIPE_QUX = r"\\.\pipe\qux"

PIPE_OPEN_MODE = win32pipe.PIPE_ACCESS_DUPLEX
PIPE_MODE = win32pipe.PIPE_TYPE_MESSAGE | win32pipe.PIPE_READMODE_MESSAGE | win32pipe.PIPE_WAIT
PIPE_MAX_INSTANCE = 10
PIPE_BUF_SIZE = 65536
PIPE_TIMEOUT = 0
PIPE_SECURITY = None

PIPE_SET_MODE = win32pipe.PIPE_READMODE_MESSAGE
PIPE_SET_COLLECTION_MAX_COUNT = None
PIPE_SET_COLLECTION_TIMEOUT = None

FILE_ACCESS = win32file.GENERIC_READ | win32file.GENERIC_WRITE
FILE_SHARE_MODE = win32file.FILE_SHARE_READ | win32file.FILE_SHARE_WRITE
FILE_SECURITY = None
FILE_CREATION = win32file.OPEN_EXISTING
FILE_FLAGS = 0
FILE_TEMPLATE = None

G_foo_server_running = False
G_foo_pipe = None
G_bar_server_running = False

#================================
#
#
def launcher():

    print("pipe launcher begin")

    kill = False
    task = []

    fool = threading.Thread(target=foo_server_launcher, args=(lambda: kill,))
    task.append(fool)
    fool.start()

    #barl = threading.Thread(target=bar_server_launcher, args=(lambda: kill,))
    #task.append(barl)
    #barl.start()

    while True:
        if  check_quit():
            kill = True
            for t in task:
                t.join()
            break;

    print("pipe launcher end")
    return

#================================
#
#
def foo_server_launcher(kill_me):

    print("foo-s: pipe launcher begin")

    global G_foo_server_running
    kill = False
    task = []

    while True:

        if  not G_foo_server_running:

            pipe = win32pipe.CreateNamedPipe(
                PIPE_FOO,           # pipe name
                PIPE_OPEN_MODE,     # pipe open mode
                PIPE_MODE,          # pipe mode
                PIPE_MAX_INSTANCE,  # max instance
                PIPE_BUF_SIZE,      # out buffer size
                PIPE_BUF_SIZE,      # in  buffer size
                PIPE_TIMEOUT,       # timeout
                PIPE_SECURITY       # secuity attributes
            )
            print("foo-s: waiting for client")
            win32pipe.ConnectNamedPipe(pipe, None) #---- blocking ----
            print("foo-s: got client")

            foox = threading.Thread(target=foo_server, args=(pipe, lambda: kill))
            task.append(foox)
            foox.start()

            G_foo_server_running = True

        if  kill_me():
            kill = True
            for t in task:
                t.join()
            break

    print("foo-s: pipe launcher end")
    return

#================================
#
#
def foo_server(pipe, kill_me):

    print("foo-s: pipe server begin")

    global G_foo_server_running
    global G_foo_pipe
    G_foo_pipe = pipe
    count = 0

    try:
        while True:
            print(f"foo-s: write {count}")
            d = str.encode(f"{count}")
            win32file.WriteFile(pipe, d)
            time.sleep(1)

            count += 1

            if  kill_me():
                break

    except pywintypes.error as e:
        if  e.args[0] == 232:
            print("foo-s: the pipe is being closed")
            G_foo_server_running = False

    G_foo_pipe = None
    print("foo-s: pipe server end")
    return

#================================
#
#
def foo_client():

    print("foo-c: pipe client begin")

    quit = False

    while not quit:
        try:
            h = win32file.CreateFile(
                PIPE_FOO,           # pipe file name
                FILE_ACCESS,        # desired access mode
                FILE_SHARE_MODE,    # share mode
                FILE_SECURITY,      # security attributes
                FILE_CREATION,      # creation disposition
                FILE_FLAGS,         # flag and attributes
                FILE_TEMPLATE       # template file
            )

            r = win32pipe.SetNamedPipeHandleState(
                h, # pipe handle
                PIPE_SET_MODE,                  # mode
                PIPE_SET_COLLECTION_MAX_COUNT,  # max collection count
                PIPE_SET_COLLECTION_TIMEOUT     # collection data timeout
            )

            if  r == 0:
                e = win32api.GetLastError()
                print(f"foo-c: SetNamedPipeHandleState return code = {e}")
            
            while True:
                d = win32file.ReadFile(h, PIPE_BUF_SIZE) #---- blocking ----
                print(f"foo-c: read {d}")

                if  check_quit():
                    quit = True
                    break;

        except pywintypes.error as e:
            if  e.args[0] == 2:
                print("foo-c: no pipe, trying again in a sec")
                time.sleep(1)
            elif e.args[0] == 109:
                print("foo-c: broken pipe, bye bye")
                quit = True

    print("foo-c: pipe client end")
    return

#================================
#
#
def bar_server_launcher(kill_me):

    print("bar-s: pipe launcher begin")

    global G_bar_server_running
    kill = False
    task = []

    while True:

        if  not G_bar_server_running:

            pipe = win32pipe.CreateNamedPipe(
                PIPE_BAR,           # pipe name
                PIPE_OPEN_MODE,     # pipe open mode
                PIPE_MODE,          # pipe mode
                PIPE_MAX_INSTANCE,  # max instance
                PIPE_BUF_SIZE,      # out buffer size
                PIPE_BUF_SIZE,      # in  buffer size
                PIPE_TIMEOUT,       # timeout
                PIPE_SECURITY       # secuity attributes
            )
            print("bar-s: waiting for client")
            win32pipe.ConnectNamedPipe(pipe, None) #---- blocking ----
            print("bar-s: got client")

            barx = threading.Thread(target=bar_server, args=(pipe, lambda: kill))
            task.append(barx)
            barx.start()

            G_bar_server_running = True

        if  kill_me():
            kill = True
            for t in task:
                t.join()
            break

    print("bar-s: pipe launcher end")
    return

#================================
#
#
def bar_server(pipe, kill_me):

    print("bar-s: pipe server begin")

    global G_bar_server_running
    
    try:
        while True:
            d = win32file.ReadFile(pipe, PIPE_BUF_SIZE) #---- blocking ----
            print(f"bar-s: receive {d}")

            if  kill_me():
                break

    except pywintypes.error as e:
        if e.args[0] == 109:
            print("bar-c: broken pipe, bye bye")
            G_bar_server_running = False

    print("bar-s: pipe server end")
    return

#================================
#
#
def bar_client():

    print("bar-c: pipe client begin")

    count = 0
    quit  = False

    while not quit:
        try:
            h = win32file.CreateFile(
                PIPE_BAR,           # pipe file name
                FILE_ACCESS,        # desired access mode
                FILE_SHARE_MODE,    # share mode
                FILE_SECURITY,      # security attributes
                FILE_CREATION,      # creation disposition
                FILE_FLAGS,         # flag and attributes
                FILE_TEMPLATE       # template file
            )

            r = win32pipe.SetNamedPipeHandleState(
                h, # pipe handle
                PIPE_SET_MODE,                  # mode
                PIPE_SET_COLLECTION_MAX_COUNT,  # max collection count
                PIPE_SET_COLLECTION_TIMEOUT     # collection data timeout
            )

            if  r == 0:
                e = win32api.GetLastError()
                print(f"bar-c: SetNamedPipeHandleState return code = {e}")
            
            while True:
                print(f"bar-c: send {count}")
                d = str.encode(f"{count}")
                win32file.WriteFile(h, d)
                time.sleep(1)

                count += 1

                if  check_quit():
                    quit = True
                    break;

        except pywintypes.error as e:
            if  e.args[0] == 2:
                print("bar-c: no pipe, trying again in a sec")
                time.sleep(1)
            elif e.args[0] == 109:
                print("bar-c: broken pipe, bye bye")
                quit = True

        if  check_quit():
            quit = True
            break;

    print("bar-c: pipe client end")
    return

#================================
#
#
def check_quit():

    if  msvcrt.kbhit():
        c = msvcrt.getch()
        print(f"you typed {c.decode()}")
        if  c == b'q':
            return True

    return False

#
# eof
#
