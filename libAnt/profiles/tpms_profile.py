from libAnt.core import lazyproperty
from libAnt.profiles.profile import ProfileMessage


class TPMSProfileMessage(ProfileMessage):
    """ Message from Tire Pressure Monitor Sensor"""

    def __init__(self, msg, previous):
        super().__init__(msg, previous)
        self.mfg_id = previous.mfg_id if previous else None
        self.pressure = previous.pressure if previous else None
        self.location = previous.location if previous else None

        self.is_main_data_page = msg.content[0] == 0x01 
        self.is_mfg_info_page = msg.content[0] == 0x50

    @lazyproperty
    def manufacturer(self):
        if self.is_mfg_info_page:
            self.mfg_id = int(self.msg.content[5]<<8 | self.msg.content[4])
        return self.mfg_id

    @lazyproperty
    def tire_pressure(self):
        if self.is_main_data_page:
            lsb = self.msg.content[6]
            msb = self.msg.content[7]
            self.pressure = msb << 8 | lsb
        return self.pressure

    @lazyproperty
    def sensor_location(self):
        if self.is_main_data_page:
            location_bits = self.msg.content[1] & 0b1111
            if location_bits == 1:
                self.location = 'FRONT'
            if location_bits == 2:
                self.location = 'REAR'
        return self.location

    def __str__(self):
        return super().__str__()

    def json(self):
        msg = super().json()
        msg['deviceType']='TPMS'
        msg['manufacturer_id']=self.manufacturer
        msg['sensorData']={'tire_pressure_mbar': self.tire_pressure, 'sensor_location': self.sensor_location}
        return msg