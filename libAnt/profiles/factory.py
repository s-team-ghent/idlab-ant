from threading import Lock

from libAnt.message import BroadcastMessage
from libAnt.profiles.power_profile import PowerProfileMessage
from libAnt.profiles.speed_cadence_profile import SpeedAndCadenceProfileMessage
from libAnt.profiles.heartrate_profile import HeartRateProfileMessage
from libAnt.profiles.muscle_oxygen_profile import MuscleOxygenProfileMessage
from libAnt.profiles.running_dynamics_profile import RunningDynamicsProfileMessage
from libAnt.profiles.core_temp import CoreTemperatureProfileMessage
from libAnt.profiles.tpms_profile import TPMSProfileMessage
from libAnt.profiles.running_dynamics_profile import RunningDynamicsProfileMessage
from libAnt.profiles.ctf_profile import CTFProfileMessage
from libAnt.profiles.cadence_profile import CadenceProfileMessage

from libAnt.profiles.manufacturer_profile import MfgProfileMessage

class Factory:
    types = {
        120: HeartRateProfileMessage,
        121: SpeedAndCadenceProfileMessage,
        122: CadenceProfileMessage,
        11: PowerProfileMessage,
        31: MuscleOxygenProfileMessage,
        30: RunningDynamicsProfileMessage,
        48: TPMSProfileMessage,
        127: CoreTemperatureProfileMessage
        #50: MfgProfileMessage
    }

    def __init__(self, callback=None):
        self._filter = None
        self._lock = Lock()
        self._messages = {}
        self._callback = callback
        self.slope_offsets = {}
        self.mfg_ids = {}

    def enableFilter(self):
        with self._lock:
            if self._filter is None:
                self._filter = {}

    def disableFilter(self):
        with self._lock:
            if self._filter is not None:
                self._filter = None

    def clearFilter(self):
        with self._lock:
            if self._filter is not None:
                self._filter.clear()

    def addToFilter(self, deviceNumber: int):
        with self._lock:
            if self._filter is not None:
                self._filter[deviceNumber] = True

    def removeFromFilter(self, deviceNumber: int):
        with self._lock:
            if self._filter is not None:
                if deviceNumber in self._filter:
                    del self._filter[deviceNumber]

    def parseMessage(self, msg: BroadcastMessage):
        with self._lock:
            if self._filter is not None:
                if msg.deviceNumber not in self._filter:
                    return
            if msg.deviceType in Factory.types:
                num = msg.deviceNumber
                type = msg.deviceType
                deviceId = msg.transType>>4<<16 | msg.deviceNumber
                if type == 11: # Quick patch to filter out power messages with non-power info
                    #print("Power message - type {}".format(hex(msg.content[0])))
                    if msg.content[0] == 0x20: #SRM CTF profile
                        offset_value = self.slope_offsets[deviceId] if deviceId in self.slope_offsets else None
                        pmsg = CTFProfileMessage(msg, self._messages[(num, type)] if (num, type) in self._messages else None, offset_value)
                    elif msg.content[0] == 0x01: # General callibration response
                        offset_msb = msg.content[6]
                        offset_lsb = msg.content[7]
                        offset = offset_msb<<8 | offset_lsb
                        #print("Received a offset from {} of {}".format(deviceId, offset))
                        self.slope_offsets[deviceId]=offset
                        return
                    elif msg.content[0] == 0x50:
                        print("mfg info for {}".format(msg.deviceNumber))
                        print("{}".format(msg.content[5]<<8 | msg.content[4]))
                        self.mfg_ids[deviceId] = int(msg.content[5]<<8 | msg.content[4])
                        return
                    elif msg.content[0] != 16:
                        return
                    else:
                        mfg_id = self.mfg_ids[deviceId] if deviceId in self.mfg_ids else None
                        pmsg = self.types[type](msg, self._messages[(num, type)] if (num, type) in self._messages else None, mfg_id)
                else:
                    pmsg = self.types[type](msg, self._messages[(num, type)] if (num, type) in self._messages else None)
                self._messages[(num, type)] = pmsg
                if pmsg and callable(self._callback):
                    self._callback(pmsg)

    def reset(self):
        with self._lock:
            self._messages = {}