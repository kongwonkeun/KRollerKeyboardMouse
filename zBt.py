#
#
#

import sys
import bluetooth
import win32file
import msvcrt
import threading

import zPipe
import zMouse
import zKey

UUID_RFCOMM = "00000003-0000-1000-8000-00805F9B34FB"
UUID_SPP = "00001101-0000-1000-8000-00805F9B34FB"

BT_NAME = "HC-05"
BT_ADDR = "98:D3:91:FD:50:03"

G_connected = False
G_found = False

#================================
#
#
class BtRxThread(threading.Thread):

    def __init__(self, sock):
        threading.Thread.__init__(self)
        self.sock = sock
        self.rotation = 0
        self.dir = 0
        self.s = 0
        self.r = 0
        self.d = 0
        self.f = True
        return

    def stop(self):
        self.f = False
        return

    #============================
    #
    #
    def run(self):
        #---- rx loop ----
        while (self.f):
            rx = self.sock.recv(1024)   # rx is byte stream

            if  zPipe.G_foo_server_running:
                win32file.WriteFile(zPipe.G_foo_pipe, rx)

            if  rx:
                rd = rx.decode()        # rd is str
                #print(rd, end='', flush=True)
                for i in range(len(rd)):
                    self.state_machine(rd[i])
        self.sock.close()
        return

    def state_machine(self, d):
        b = ord(d)
        if   b == 82: self.s = 1; self.r = 0 # 82 = 'R' of 'Rnnn'
        elif b == 68: self.s = 5; self.d = 0 # 68 = 'D' of 'Dnnn'
        else:
            if    self.s == 1: self.s = 2; self.r = (b - 48)
            elif  self.s == 2: self.s = 3; self.r = (self.r * 10) + (b - 48)
            elif  self.s == 3: self.s = 4; self.r = (self.r * 10) + (b - 48)
            elif  self.s == 5: self.s = 6; self.d = (b - 48)
            elif  self.s == 6: self.s = 7; self.d = (self.d * 10) + (b - 48)
            elif  self.s == 7: self.s = 8; self.d = (self.d * 10) + (b - 48)
            else: pass

        if  self.s == 4:
            self.rotation = self.r
            #print(f"R:{self.ratation}")
            return

        if  self.s == 8:
            self.dir = self.d
            x = self.dir - 19
            y = self.rotation / 30
            #print(f"D:{self.dir}")
            #zMouse.move(x, y)
        return

#================================
#
#
class Bt(object):

    def __init__(self):
        self.sock = None
        self.s = 0
        self.r = 0
        self.d = 0
        return

    def stop(self):
        print("stop BtRxThread")
        self.thread.stop()
        return

    #============================
    #
    #
    def connect(self):

        global G_found
        print("inquery")
        devices = bluetooth.discover_devices(duration=8, lookup_names=True, flush_cache=True, lookup_class=False)
        print(f"found {len(devices)} devices")

        n = 1
        for addr, name in devices:
            try:
                print(f"{n}: {addr} - {name}")
            except UnicodeEncodeError:
                print(f"{n}: {addr} + {name.encode('utf-8', 'replace')}")
            n += 1

        #print("select device to connect > ", end='', flush=True)
        #c = msvcrt.getch()
        #print(c.decode())
        #n = int(c.decode())

        n = 1
        for addr, name in devices:
            if  name == BT_NAME:
                break;
            n += 1
            if  n > len(devices):
                G_found = False
                return

        print("found kroller device")
        G_found = True
        self.addr = devices[n-1][0]
        self.name = devices[n-1][1]
        print(f"try to connect to kroller ({self.name}, {self.addr}) ...")
        self.spp_client()
        return

    #============================
    #
    #
    def sdp(self, target):

        print("sdp")
        if  target == 'all':
            target = None
        services = bluetooth.find_service(address=target)

        if  len(services) > 0:
            print("found %d services on %s" % (len(services), target))
        else:
            print("no services found")

        for s in services:
            print("service name: %s" % (s['name']))
            print("host: %s" % (s['host']))
            print("description: %s" % (s['description']))
            print("provider: %s" % (s['provider']))
            print("protocol: %s" % (s['protocol']))
            print("channel/psm: %s" % (s['port'])) # psm - protocol and service multiplexer
            print("profiles: %s" % (s['profiles']))
            print("service classes: %s" % (s['service-classes']))
            print("service id: %s" % (s['service-id']))
        return

    #============================
    #
    #
    def spp_client(self):

        global G_connected
        print("spp client")
        print(f"searching for spp server on {self.addr}")

        uuid = UUID_SPP
        services = bluetooth.find_service(uuid=uuid, address=self.addr)

        if  len(services) == 0:
            print("could not find the spp server service")
            G_connected = False
            return

        s = services[0]
        port = s['port']
        name = s['name']
        host = s['host']
        print(f"connecting to {name} on {host}")

        self.sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        self.sock.connect((host, port))
        print("connected")
        G_connected = True

        #---- thread ----
        self.thread = BtRxThread(self.sock)
        self.thread.start()
        return

#
# eof
#