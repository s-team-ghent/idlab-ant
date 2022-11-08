from libAnt.core import lazyproperty
from libAnt.profiles.profile import ProfileMessage


class RunningDynamicsProfileMessage(ProfileMessage):
    """ Message from Running Dynamics device """

    def __init__(self, msg, previous):
        super().__init__(msg, previous)
        self.vertical_oscillation = previous.vertical_oscillation if previous else None
        self.vertical_ratio = previous.vertical_ratio if previous else None
        self.ground_contact_time = previous.ground_contact_time if previous else None
        self.stride_length = previous.stride_length if previous else None
        self.cadence = previous.cadence if previous else None
        self.mfg_id = previous.mfg_id if previous else None
        
        self.is_data_page_a = msg.content[0] == 0x00 
        self.is_data_page_b = msg.content[0] == 0x01
        self.is_mfg_info_page = msg.content[0] == 0x50
    
    @lazyproperty
    def calculated_vertical_oscillation(self):
        if self.is_data_page_a:
            oscillation_lsb = self.msg.content[3]
            osciallation_msb = self.msg.content[4] & 0b111
            self.vertical_oscillation = osciallation_msb << 3 | oscillation_lsb
        return self.vertical_oscillation

    @lazyproperty
    def calculated_gct(self):
        if self.is_data_page_a:
            gct_msb = self.msg.content[5]
            gct_lsb = (self.msg.content[4] & 0b11100000)>>5
            self.ground_contact_time = gct_msb << 3 | gct_lsb
        return self.ground_contact_time

    @lazyproperty
    def calculated_vertical_ratio(self):
        if self.is_data_page_b:
            vertical_ratio_msb = self.msg.content[3] & 0b111
            vertical_ratio_lsb = (self.msg.content[2] & 0b11110000)>>4
            self.vertical_ratio = vertical_ratio_msb << 4 | vertical_ratio_lsb
        return self.vertical_ratio

    @lazyproperty
    def calculated_stride_length(self):
        if self.is_data_page_b:
            steplength_msb = self.msg.content[5] & 0b11111
            steplength_lsb = self.msg.content[4] 
            self.stride_length = steplength_msb << 8 | steplength_lsb
        return self.stride_length

    @lazyproperty
    def calculated_cadence(self):
        if self.is_data_page_a:
            self.cadence = self.msg.content[1]
        return self.cadence

    @lazyproperty
    def manufacturer(self):
        if self.is_mfg_info_page:
            self.mfg_id = int(self.msg.content[5]<<8 | self.msg.content[4])
        return self.mfg_id

    def __str__(self):
        return super().__str__()

    def json(self):
        msg = super().json()
        msg['deviceType']='RunningDynamics'
        msg['manufacturer_id']=self.manufacturer
        msg['sensorData']={
            'ground_contact_time': self.calculated_gct, 
            'vertical_ratio': self.calculated_vertical_ratio,
            'vertical_oscillation': self.calculated_vertical_oscillation,
            'stride_length': self.calculated_stride_length,
            'run_cadence': self.calculated_cadence
            }
        return msg