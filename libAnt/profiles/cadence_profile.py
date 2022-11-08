from libAnt.core import lazyproperty
from libAnt.profiles.profile import ProfileMessage


class CadenceProfileMessage(ProfileMessage):
    """ Message from Cadence sensor """

    def __init__(self, msg, previous):
        super().__init__(msg, previous)
        self.staleCadenceCounter = previous.staleCadenceCounter if previous is not None else 0
        self.totalRevolutions = previous.totalRevolutions + self.cadenceRevCountDiff if previous is not None else 0

        if self.previous is not None:
            if self.cadenceEventTime == self.previous.cadenceEventTime:
                self.staleCadenceCounter += 1
            else:
                self.staleCadenceCounter = 0

    maxCadenceEventTime = 65536
    maxSpeedRevCount = 65536
    maxCadenceRevCount = 65536
    maxstaleCadenceCounter = 7

    def json(self):
        if self.msg.content[0]==0x00:
            msg =  super().json()
            msg['deviceType']='Cad'
            msg['sensorData']={'cadence': self.cadence}
            return msg
        
    def __str__(self):
        ret = '{} Cadence: {:.2f}rpm (avg: {:.2f}rpm)\n'.format(super().__str__(), self.cadence, self.averageCadence)
        ret += '{} Total Revolutions: {:d}'.format(super().__str__(), self.totalRevolutions)
        return ret

    @lazyproperty
    def cadenceEventTime(self):
        """ Represents the time of the last valid bike cadence event (1/1024 sec) """
        return (self.msg.content[5] << 8) | self.msg.content[4]

    @lazyproperty
    def cumulativeCadenceRevolutionCount(self):
        """ Represents the total number of pedal revolutions """
        return (self.msg.content[7] << 8) | self.msg.content[6]


    @lazyproperty
    def cadenceEventTimeDiff(self):
        if self.previous is None:
            return 0
        elif self.cadenceEventTime < self.previous.cadenceEventTime:
            # Rollover
            return (self.cadenceEventTime - self.previous.cadenceEventTime) + self.maxCadenceEventTime
        else:
            return self.cadenceEventTime - self.previous.cadenceEventTime


    @lazyproperty
    def cadenceRevCountDiff(self):
        if self.previous is None:
            return 0
        elif self.cumulativeCadenceRevolutionCount < self.previous.cumulativeCadenceRevolutionCount:
            # Rollover
            return (
                       self.cumulativeCadenceRevolutionCount - self.previous.cumulativeCadenceRevolutionCount) + self.maxCadenceRevCount
        else:
            return self.cumulativeCadenceRevolutionCount - self.previous.cumulativeCadenceRevolutionCount

    @lazyproperty
    def cadence(self):
        """
        :return: RPM
        """
        if self.previous is None:
            return 0
        if self.cadenceEventTime == self.previous.cadenceEventTime:
            if self.staleCadenceCounter > self.maxstaleCadenceCounter:
                return 0
            return self.previous.cadence
        return self.cadenceRevCountDiff * 1024 * 60 / self.cadenceEventTimeDiff

    @lazyproperty
    def averageCadence(self):
        """
        Returns the average cadence since the first message
        :return: RPM
        """
        if self.firstTimestamp == self.timestamp:
            return self.cadence
        return self.totalRevolutions * 60 / (self.timestamp - self.firstTimestamp)
