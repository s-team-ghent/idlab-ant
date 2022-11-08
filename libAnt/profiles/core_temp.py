from libAnt.core import lazyproperty
from libAnt.profiles.profile import ProfileMessage


class CoreTemperatureProfileMessage(ProfileMessage):
    """ Message from Core Temperature Sensor"""

    def __init__(self, msg, previous):
        super().__init__(msg, previous)
        self.core_temperature = previous.core_temperature if previous else None
        self.mfg_id = previous.mfg_id if previous else None
        self.skin_temp = previous.skin_temp if previous else None

        self.is_main_datapage = msg.content[0] == 0x01
        self.is_mfg_info_page = msg.content[0] == 0x50

    @lazyproperty
    def manufacturer(self):
        if self.is_mfg_info_page:
            self.mfg_id = int(self.msg.content[5]<<8 | self.msg.content[4])
        return self.mfg_id

    @lazyproperty
    def temperature(self):
        if self.is_main_datapage:
            lsb = self.msg.content[6]
            msb = self.msg.content[7]
            self.core_temperature = (msb << 8 | lsb)/100
        return self.core_temperature

    @lazyproperty
    def skin_temperature(self):
        if self.is_main_datapage:
            lsb = self.msg.content[3]
            msn = self.msg.content[4] & 0b11110000
            self.skin_temp = (msn << 4 | lsb)/20
        return self.skin_temp

    def __str__(self):
        return super().__str__()

    def json(self):
        msg = super().json()
        msg['deviceType']='CORE'
        msg['manufacturer_id']=self.manufacturer
        msg['sensorData']={"core_temperature_c": self.temperature, "skin_temperature_c": self.skin_temperature}
        return msg