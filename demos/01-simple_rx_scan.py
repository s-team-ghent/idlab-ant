#!/usr/bin/env python3
from time import sleep

from libAnt.drivers.serial import SerialDriver
from libAnt.drivers.usb import USBDriver
from libAnt.node import Node


def callback(msg):
    print(msg.deviceType)
    print(msg.deviceNumber)
    print(msg.rssi)
    print(str(msg.rxTimestamp))
    print(str(msg.content[3])+"RPM")
    print(str((msg.content[7] << 8) | msg.content[6])+"W")
    print(bytearray(msg.extendedContent).hex())


def eCallback(e):
    print(e)

# for USB driver
# with Node(USBDriver(vid=0x0FCF, pid=0x1008), 'MyNode') as n:

# for serial driver
with Node(USBDriver(vid=0x0FCF, pid=0x1008), 'MyNode') as n:
    n.enableRxScanMode()
    n.start(callback, eCallback)
    sleep(30)  # Listen for 30sec
