from libAnt.core import lazyproperty
from libAnt.profiles.profile import ProfileMessage


class MfgProfileMessage(ProfileMessage):
    """ Manufacturer info """

    def __init__(self, msg, previous):
        super().__init__(msg, previous)

    def json(self):
        msg =  super().json()
        return msg
        
    def __str__(self):
        return ""
