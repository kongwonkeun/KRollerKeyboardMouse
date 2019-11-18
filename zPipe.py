#
#
#

import sys
import time
import win32api, win32pipe, win32file, pywintypes
import ctypes
import msvcrt
import threading

import zKey

PIPE_FOOBAR = r"\\.\pipe\foobar"
PIPE_FOO = r"\\.\pipe\foo"
PIPE_BAR = r"\\.\pipe\bar"

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

G_foobar_server_running = False
G_foo_server_running = False
G_bar_server_running = False

G_foobar_pipe = None
G_foo_pipe = None

#================================
#
#
def launcher():

    print("pipe launcher begin")
    kill = False
    task = []

    foobarl = threading.Thread(target=foobar_server_launcher, args=(lambda: kill,))
    task.append(foobarl)
    foobarl.start()

    fool = threading.Thread(target=foo_server_launcher, args=(lambda: kill,))
    task.append(fool)
    fool.start()

    #---- kong ---- for future usage
    #barl = threading.Thread(target=bar_server_launcher, args=(lambda: kill,))
    #task.append(barl)
    #barl.start()
    #----

    while True:
        if  check_quit():
            kill = True
            for t in task:
                t.join()
            break;

        time.sleep(1)

    print("pipe launcher end")
    return

#================================
#
#
def foobar_server_launcher(kill_me):

    global G_foobar_server_running

    print("pipe-foobar launcher begin")
    kill = False
    task = []

    while True:

        if  not G_foobar_server_running:

            p = win32pipe.CreateNamedPipe(
                PIPE_FOOBAR,        # pipe name
                PIPE_OPEN_MODE,     # pipe open mode
                PIPE_MODE,          # pipe mode
                PIPE_MAX_INSTANCE,  # max instance
                PIPE_BUF_SIZE,      # out buffer size
                PIPE_BUF_SIZE,      # in  buffer size
                PIPE_TIMEOUT,       # timeout
                PIPE_SECURITY       # secuity attributes
            )
            print("foobar: waiting for client")
            win32pipe.ConnectNamedPipe(p, None) #---- blocking ----
            print("foobar: got client")

            x = threading.Thread(target=foobar_server, args=(p, lambda: kill))
            task.append(x)
            x.start()

            G_foobar_server_running = True

        if  kill_me():
            kill = True
            for t in task:
                t.join()
            break

        time.sleep(1)

    print("pipe-foobar launcher end")
    return

#================================
#
#
def foobar_server(pipe, kill_me):

    global G_foobar_server_running
    global G_foobar_pipe

    print("foobar: server begin")
    G_foobar_pipe = pipe
    count = 0

    try:
        while True:
            #---- task ----
            #print(f"foobar: write {count}")
            #d = str.encode(f"{count}")   # encode to byte stream
            #win32file.WriteFile(pipe, d) # write
            win32file.WriteFile(pipe, b"T") # write
            time.sleep(1)
            #----

            count += 1

            if  G_foobar_pipe == None:
                G_foobar_server_running = False
                break;

            if  kill_me():
                break

    except  pywintypes.error as e:
        if  e.args[0] == 232:
            print("foobar: pipe is being closed")
            G_foobar_server_running = False

    G_foobar_pipe = None
    print("foobar: server end")
    return

#================================
#
#
def foobar_client():

    print("foobar: client begin")

    quit = False

    while not quit:
        try:
            h = win32file.CreateFile(
                PIPE_FOOBAR,        # pipe file name
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
                print(f"foobar: SetNamedPipeHandleState return code = {e}")
            
            while True:
                #---- task ----
                d = win32file.ReadFile(h, PIPE_BUF_SIZE) #---- blocking ---- read byte stream
                print(f"foobar: read {d[1].decode()}") # decide to string
                #----

                if  check_quit():
                    quit = True
                    break;

        except  pywintypes.error as e:
            if  e.args[0] == 2:
                print("foobar: there is no pipe (try again in a sec)")
                time.sleep(1)
            elif e.args[0] == 109:
                print("foobar: broken pipe")
                quit = True

    print("foobar: client end")
    return

#================================
#
#
def foo_server_launcher(kill_me):

    global G_foo_server_running

    print("pipe-foo launcher begin")
    kill = False
    task = []

    while True:

        if  not G_foo_server_running:

            p = win32pipe.CreateNamedPipe(
                PIPE_FOO,           # pipe name
                PIPE_OPEN_MODE,     # pipe open mode
                PIPE_MODE,          # pipe mode
                PIPE_MAX_INSTANCE,  # max instance
                PIPE_BUF_SIZE,      # out buffer size
                PIPE_BUF_SIZE,      # in  buffer size
                PIPE_TIMEOUT,       # timeout
                PIPE_SECURITY       # secuity attributes
            )
            print("foo: waiting for client")
            win32pipe.ConnectNamedPipe(p, None) #---- blocking ----
            print("foo: got client")

            x = threading.Thread(target=foo_server, args=(p, lambda: kill))
            task.append(x)
            x.start()

            G_foo_server_running = True

        if  kill_me():
            kill = True
            for t in task:
                t.join()
            break

        time.sleep(1)

    print("pipe-foo launcher end")
    return

#================================
#
#
def foo_server(pipe, kill_me):

    global G_foo_server_running
    global G_foo_pipe

    print("foo: server begin")
    G_foo_pipe = pipe
    count = 0

    try:
        while True:
            #---- task ----
            #print(f"foo: write {count}")
            #d = str.encode(f"{count}")   # encode to byte stream
            #win32file.WriteFile(pipe, d) # write
            win32file.WriteFile(pipe, b"T") # write
            time.sleep(1)
            #----

            count += 1

            if  G_foo_pipe == None:
                G_foo_server_running = False
                break;

            if  kill_me():
                break

    except  pywintypes.error as e:
        if  e.args[0] == 232:
            print("foo: pipe is being closed")
            G_foo_server_running = False

    G_foo_pipe = None
    print("foo: server end")
    return

#================================
#
#
def foo_client():

    print("foo: client begin")

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
                print(f"foo: SetNamedPipeHandleState return code = {e}")
            
            while True:
                #---- task ----
                d = win32file.ReadFile(h, PIPE_BUF_SIZE) #---- blocking ---- read byte stream
                print(f"foo: read {d[1].decode()}") # decide to string
                #----

                if  check_quit():
                    quit = True
                    break;

        except  pywintypes.error as e:
            if  e.args[0] == 2:
                print("foo: there is no pipe (try again in a sec)")
                time.sleep(1)
            elif e.args[0] == 109:
                print("foo: broken pipe")
                quit = True

    print("foo: client end")
    return

#================================
#
#
def bar_server_launcher(kill_me):

    global G_bar_server_running

    print("pipe-bar launcher begin")
    kill = False
    task = []

    while True:

        if  not G_bar_server_running:

            p = win32pipe.CreateNamedPipe(
                PIPE_BAR,           # pipe name
                PIPE_OPEN_MODE,     # pipe open mode
                PIPE_MODE,          # pipe mode
                PIPE_MAX_INSTANCE,  # max instance
                PIPE_BUF_SIZE,      # out buffer size
                PIPE_BUF_SIZE,      # in  buffer size
                PIPE_TIMEOUT,       # timeout
                PIPE_SECURITY       # secuity attributes
            )
            print("bar: waiting for client")
            win32pipe.ConnectNamedPipe(p, None) #---- blocking ----
            print("bar: got client")

            x = threading.Thread(target=bar_server, args=(p, lambda: kill))
            task.append(x)
            x.start()

            G_bar_server_running = True

        if  kill_me():
            kill = True
            for t in task:
                t.join()
            break

        time.sleep(1)

    print("pipe-bar launcher end")
    return

#================================
#
#
def bar_server(pipe, kill_me):

    global G_bar_server_running

    print("bar: server begin")
    
    try:
        while True:
            #---- task ----
            d = win32file.ReadFile(pipe, PIPE_BUF_SIZE) #---- blocking ---- receive byte stream
            print(f"bar: receive {d[1].decode()}") # decode to string
            #----

            if  kill_me():
                break

    except  pywintypes.error as e:
        if  e.args[0] == 109:
            print("bar: broken pipe")
            G_bar_server_running = False

    print("bar: server end")
    return

#================================
#
#
def bar_client():

    print("bar: client begin")

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
                print(f"bar: SetNamedPipeHandleState return code = {e}")
            
            while True:
                #---- task ----
                print(f"bar: send {count}")
                d = str.encode(f"{count}") # encode to byte stream
                win32file.WriteFile(h, d)  # send
                time.sleep(1)
                #----

                count += 1

                if  check_quit():
                    quit = True
                    break;

        except  pywintypes.error as e:
            if  e.args[0] == 2:
                print("bar: there is no pipe (try again in a sec)")
                time.sleep(1)
            elif e.args[0] == 109:
                print("bar: broken pipe")
                quit = True

        if  check_quit():
            quit = True
            break;

    print("bar: client end")
    return

#================================
#
#
def check_quit():

    if  msvcrt.kbhit():
        c = msvcrt.getch()
        #print(f"you typed {c.decode()}")
        if  c == b'q':
            return True

    return False

#
# eof
#
