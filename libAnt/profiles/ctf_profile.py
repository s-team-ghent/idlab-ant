from libAnt.core import lazyproperty
from libAnt.profiles.profile import ProfileMessage


class CTFProfileMessage(ProfileMessage):
    """ Message from Power Meter """

    maxTorqueTicks = 65536
    maxEventCount = 256
    maxTimestamp = 65400

    def __init__(self, msg, previous, offset_value):
        self.offset = offset_value if offset_value else 0.0

        super().__init__(msg, previous)

    def __str__(self):
        return super().__str__() + ' Power: {0:.0f}W'.format(0) + ' Cadence: {0:.0f}RPM'.format(self.calculatedCadence)

    def json(self):
        msg = super().json()
        msg['deviceType']='powerCTF'
        msg['sensorData']={'power': self.calculatedPower, 'cadence': self.calculatedCadence, 'torque': self.calculatedTorque, 'offset': self.offset}
        return msg
        
    @lazyproperty
    def dataPageNumber(self):
        """
        :return: Data Page Number (int)
        """
        return self.msg.content[0]

    @lazyproperty
    def eventCount(self):
        """
        The update event count field is incremented each time the information in the message is updated.
        There are no invalid values for update event count.
        The update event count in this message refers to updates of the standard CTF main data page (0x20)
        :return: Power Event Count
        """
        return self.msg.content[1]

    @lazyproperty
    def slope(self):
        """
        The slope is a configuration value required by the display to convert torque ticks into units 
        of Newton metres. It is saved to the power sensor’s flash memory during manufacturing. 
        Slope ranges in value from 10.0Nm/Hz to 50.0Nm/Hz. 
        To send slope as an integer, the slope field is sent in units of 1/10 Nm/Hz, 
        with values ranging between 100 and 500. Slope is included in every message so that special 
        messaging is not required at startup to retrieve it.
        :return: Torque seconds (Nm/Hz)
        """
        return self.msg.content[2]<<8 | self.msg.content[3]

    @lazyproperty
    def cadenceTimestamp(self):
        """
        The crank torque-frequency message uses a 2000Hz clock to time cadence events. The time stamp 
        field indicates the time of the most recent cadence event. Each time stamp tick represents
        a 500-microsecond interval. The time stamp field rolls over every 32.7 seconds.
        """
        return self.msg.content[4]<<8 | self.msg.content[5]

    @lazyproperty
    def torqueTicks(self):
        """
        The torque ticks stamp represents the most recent value of torque ticks since the last 
        registered revolution. The amount of time that the torque ticks stamp provides protection 
        against RF outage depends on torque, cadence, and calibration values. Under the most 
        extreme conditions, with maximum slope (50Nm/Hz) and maximum offset (1000Hz) there is 
        adequate buffer for transmission loss
        """
        return self.msg.content[6]<<8 | self.msg.content[7]

    @lazyproperty
    def calculatedCadence(self):
        """
        Calculates cadence value based on timestamp dif and eventcount dif
        :return: cadence (RPM)
        """
        if self.previous == None:
            return 0
        if self.eventCountDiff and self.eventCountDiff>0:
            cadencePeriod = self.timestampDiff/self.eventCountDiff*0.0005
            if cadencePeriod>0:
                return round(60/cadencePeriod)
            else:
                return 0
        else:
            return self.previous.calculatedCadence

    @lazyproperty
    def calculatedTorque(self):
        if self.previous == None:
            return 0
        if self.eventCountDiff and self.eventCountDiff>0:
            elapsedTime = self.timestampDiff*0.0005
            torqueFrequency = (1/(elapsedTime/self.torqueTickStampDiff))-self.offset
            torque = torqueFrequency/(self.slope/10)
            return torque
        return self.previous.calculatedTorque

    @lazyproperty
    def calculatedPower(self):
        if self.previous == None:
            return 0
        if self.eventCountDiff and self.eventCountDiff>0:
            torque = self.calculatedTorque
            cadence = self.calculatedCadence
            return torque*cadence*3.14159265359/30
        return self.previous.calculatedPower

    @lazyproperty
    def torqueTickStampDiff(self):
        if self.previous is None:
            return None
        elif self.torqueTicks < self.previous.torqueTicks:
            # Rollover
            return (self.torqueTicks - self.previous.torqueTicks) + self.maxTorqueTicks
        else:
            return self.torqueTicks - self.previous.torqueTicks

    @lazyproperty
    def accumulatedPowerDiff(self):
        if self.previous is None:
            return None
        elif self.accumulatedPower < self.previous.accumulatedPower:
            # Rollover
            return (self.accumulatedPower - self.previous.accumulatedPower) + self.maxAccumulatedPower
        else:
            return self.accumulatedPower - self.previous.accumulatedPower

    @lazyproperty
    def timestampDiff(self):
        if self.previous is None:
            return None
        elif self.cadenceTimestamp < self.previous.cadenceTimestamp:
            # Rollover
            return (self.cadenceTimestamp - self.previous.cadenceTimestamp) + self.maxTimestamp
        else:
            return self.cadenceTimestamp - self.previous.cadenceTimestamp

    @lazyproperty
    def eventCountDiff(self):
        if self.previous is None:
            return None
        elif self.eventCount < self.previous.eventCount:
            # Rollover
            return (self.eventCount - self.previous.eventCount) + self.maxEventCount
        else:
            return self.eventCount - self.previous.eventCount

    @lazyproperty
    def averagePower(self):
        """
        Under normal conditions with complete RF reception, average power equals instantaneous power.
        In conditions where packets are lost, average power accurately calculates power over the interval
        between the received messages
        :return: Average power (Watts)
        """
        if self.previous is None:
            return self.instantaneousPower
        if self.eventCount == self.previous.eventCount:
            return self.instantaneousPower
        return self.accumulatedPowerDiff / self.eventCountDiff
