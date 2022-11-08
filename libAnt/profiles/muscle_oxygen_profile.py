from libAnt.core import lazyproperty
from libAnt.profiles.profile import ProfileMessage


class MuscleOxygenProfileMessage(ProfileMessage):
    """ Message from Muscle Oxygen meter """

    def __init__(self, msg, previous):
        super().__init__(msg, previous)
        self.hemoglobin_MSB = previous.hemoglobin_MSB if previous else None
        self.hemoglobin_LSB = previous.hemoglobin_LSB if previous else None
        self.hemoglobin = previous.hemoglobin if previous else None
        self.saturation = previous.saturation if previous else None
        self.saturation_MSB = previous.saturation_MSB if previous else None
        self.saturation_LSB = previous.saturation_LSB if previous else None
        self.prev_saturation_MSB = previous.prev_saturation_MSB if previous else None
        self.prev_saturation_LSB = previous.prev_saturation_LSB if previous else None  
        self.previous_saturation = previous.previous_saturation if previous else None
        self.mfg_id = previous.mfg_id if previous else None

        self.is_data_page = msg.content[0] == 0x01
        self.is_mfg_info_page = msg.content[0] == 0x50
    
    @lazyproperty
    def total_hemoglobin(self):
        if self.is_data_page:
            lsb = self.msg.content[4]
            msb = self.msg.content[5]&0b1111

            self.hemoglobin_LSB = lsb
            self.hemoglobin_MSB = msb

            self.hemoglobin = (msb << 8 | lsb)*0.01

        return self.hemoglobin

    @lazyproperty
    def saturation_percentage(self):
        if self.is_data_page:
            lsb = (self.msg.content[6]&0b11000000)>>6
            msb = self.msg.content[7]

            self.saturation_MSB = msb
            self.saturation_LSB = lsb

            self.saturation = (msb<<2 | lsb)

        return self.saturation/10 if self.saturation else None

    @lazyproperty
    def previous_saturation_percentage(self):
        if self.is_data_page:
            lsb = (self.msg.content[5]&0b11110000)>>4
            msb = (self.msg.content[6]&0b111111)

            self.previous_saturation = (msb<<4 | lsb)

        return self.previous_saturation/10 if self.previous_saturation else None

    @lazyproperty
    def manufacturer(self):
        if self.is_mfg_info_page:
            self.mfg_id = int(self.msg.content[5]<<8 | self.msg.content[4])
        return self.mfg_id

    def __str__(self):
        return super().__str__() + f' SPO2: {self.total_hemoglobin:{0:.0f}}g/dl, Sat: {self.saturation_percentage}%'

    def json(self):
        msg = super().json()
        msg['deviceType']='MuscleOxygen'
        msg['manufacturer_id']=self.manufacturer
        msg['sensorData']={'SMO2': self.total_hemoglobin, 'Saturation': self.saturation_percentage, 'Previous Saturation': self.previous_saturation_percentage}
        return msg