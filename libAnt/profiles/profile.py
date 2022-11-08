from copy import deepcopy

import time

from libAnt.message import BroadcastMessage


class ProfileMessage:
    def __init__(self, msg, previous):
        self.previous = previous
        self.msg = deepcopy(msg)
        self.count = previous.count + 1 if previous is not None else 1
        self.timestamp = time.time()
        self.firstTimestamp = previous.firstTimestamp if previous is not None else self.timestamp
        self.extended_device_id = self.msg.transType>>4<<16 | self.msg.deviceNumber

    def __str__(self):
        return str(self.msg.deviceNumber)

    def json(self):
        return {"deviceID": self.msg.deviceNumber, "extendedDeviceID": self.extended_device_id, "transmissionType": self.msg.transType, "timestamp": self.timestamp}

    @staticmethod
    def decode(cls, msg: BroadcastMessage):
        if msg.deviceType in cls.match:
            cls.match[msg.deviceType]()