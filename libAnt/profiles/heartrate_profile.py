from libAnt.core import lazyproperty
from libAnt.profiles.profile import ProfileMessage


class HeartRateProfileMessage(ProfileMessage):
    """ Message from Heart Rate Monitor """

    def __init__(self, msg, previous):
        super().__init__(msg, previous)
        self.batteryStatus = previous.batteryStatus if previous else None
        self.batteryLevel = previous.batteryLevel if previous else None
        self.courseVoltage = previous.courseVoltage if previous else None
        self.fracBatteryVoltage = previous.fracBatteryVoltage if previous else None
        self.manufacturer_id = previous.manufacturer_id if previous else None
        self.serial_nr = previous.serial_nr if previous else None

        # Look if manufacturer id, battery info is included in bits 1-3
        self.check_meta_information()
    
    def check_meta_information(self):
        if self.msg.content[0]==0x02: #mfg info
            self.manufacturer_id = self.msg.content[1]
            self.serial_nr = self.msg.content[2]<<8 | self.msg.content[3]
        if self.msg.content[0]==0x07: #Battery status
            self.batteryLevel = self.calculatedBatteryLevel
            self.batteryStatus = self.calculatedBatteryStatus
            self.fracBatteryVoltage = self.calculatedFracBatteryVoltage
            self.courseVoltage = self.calculatedCourseBatteryVoltage

    @lazyproperty
    def calculatedCourseBatteryVoltage(self):
        bits = self.msg.content[3]
        course_voltage = bits & 0x0F
        return course_voltage

    @lazyproperty
    def calculatedFracBatteryVoltage(self):
        return self.msg.content[2] if self.calculatedBatteryStatus is not None else None

    @lazyproperty
    def calculatedBatteryStatus(self):
        """
        0 (0x00)Reserved for future use
        1 (0x01)Battery Status = New
        2 (0x02)Battery Status = Good
        3 (0x03)Battery Status = OK
        4 (0x04)Battery Status = Low
        5 (0x05)Battery Status = Critical
        6 (0x06)Reserved for future use
        7 (0x07)Invalid
        """
        bits = self.msg.content[3]
        status_msg = (bits & 0b1110000) >> 4

        if status_msg == 0x07:
            return None
        elif status_msg == 0x01:
            return "NEW"
        elif status_msg == 0x02:
            return "GOOD"
        elif status_msg == 0x03:
            return "OK"
        elif status_msg == 0x04:
            return "LOW"
        elif status_msg == 0x05:
            return "CRITICAL"
        else:
            return None

    @lazyproperty
    def calculatedBatteryLevel(self):
        """ 
        The battery level is used by the heart rate monitorto report the current remaining percentage 
        of battery level.The percentage value shall[MD_0010]not be set togreater than 100%. 
        Values 0x65–0xFE should not be used.If this field is not used its value should be set to 0xFF
        """
        return None if self.msg.content[1]==0xFF else self.msg.content[1]

    def __str__(self):
        return super().__str__() +  f' {self.heartrate} BPM'

    def json(self):
        msg = super().json()
        msg['deviceType']='heartrate'
        msg['manufacturer_id']=self.manufacturer_id
        msg['sensorData']={"heartrate": self.heartrate, 
                            "manufacturer_id": self.manufacturer_id, 
                            "serial_number":self.serial_nr,
                            "battery_level": self.batteryLevel,
                            "battery_status": self.batteryStatus,
                            "battery_course_v": self.courseVoltage,
                            "battery_voltage": self.fracBatteryVoltage}
        return msg

    @lazyproperty
    def heartrate(self):
        """ 
            Instantaneous heart rate. This value is
            intended to be displayed by the display
            device without further interpretation.
            If Invalid set to 0x00 
        """
        return self.msg.content[7]