from libAnt.core import lazyproperty
from libAnt.profiles.profile import ProfileMessage


class RunningDynamicsProfileMessage(ProfileMessage):
    """ Message from Running Dynamics device """

    def __init__(self, msg, previous):
        super().__init__(msg, previous)
        self.vertical_oscillation = previous.vertical_oscillation if previous else None

        self.ground_contact_balance = previous.ground_contact_balance if previous else None
        self.fractional_ground_contact_balance = previous.fractional_ground_contact_balance if previous else None

        self.vertical_ratio = previous.vertical_ratio if previous else None
        self.fractional_vertical_ratio = previous.fractional_vertical_ratio if previous else None

        self.ground_contact_time = previous.ground_contact_time if previous else None
        self.stride_length = previous.stride_length if previous else None
        
        self.cadence = previous.cadence if previous else None
        self.fractional_cadence = previous.fractional_cadence if previous else None
        
        self.vertical_oscillation = previous.vertical_oscillation if previous else None
        self.fractional_vertical_oscillation = previous.fractional_vertical_oscillation if previous else None

        self.stance_time = previous.stance_time if previous else None
        self.fractional_stance_time = previous.fractional_stance_time if previous else None

        self.step_count = previous.step_count if previous else None

        self.is_walking = previous.is_walking if previous else None

        self.module_orientation = previous.module_orientation if previous else None

        self.mfg_id = previous.mfg_id if previous else None
        
        self.is_data_page_a = msg.content[0] == 0x00 
        self.is_data_page_b = msg.content[0] == 0x01
        self.is_mfg_info_page = msg.content[0] == 0x50
    
    @lazyproperty
    def calculated_ground_contact_balance(self):
        if self.is_data_page_b:
            gct_balance = self.msg.content[1] & 0b1111111
            print("GCT balance ",gct_balance)
            frac_gct_balance_lsb = ((self.msg.content[1] & 0b10000000) >> 7)
            frac_gct_balance_msb = ((self.msg.content[2] & 0b1111)<<1)
            frac_gct_balance = (frac_gct_balance_msb | frac_gct_balance_lsb)*0.03125 
            print("frac. GCT balance ",frac_gct_balance)

            self.ground_contact_balance = gct_balance
            self.fractional_ground_contact_balance = frac_gct_balance

        if self.ground_contact_balance and self.fractional_ground_contact_balance:
            calc_gct_balance = self.ground_contact_balance + self.fractional_ground_contact_balance
            return calc_gct_balance
        else:
            return None

    @lazyproperty
    def calculated_vertical_oscillation(self):
        if self.is_data_page_a:
            oscillation_lsb = self.msg.content[3]
            oscillation_msb = (self.msg.content[4] & 0b111)<<8
            frac_oscillation = ((self.msg.content[4] & 0b11000) >> 3)*0.25
            vertical_oscillation = oscillation_msb  | oscillation_lsb
            self.vertical_oscillation = vertical_oscillation
            self.fractional_vertical_oscillation = frac_oscillation
        if self.vertical_oscillation and self.fractional_vertical_oscillation:
            calc_vertical_oscillation = self.vertical_oscillation + self.fractional_vertical_oscillation
            return calc_vertical_oscillation
        else:
            return None

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
            frac_vertical_ratio = ((self.msg.content[3] & 0b11111000) >> 3 )*0.03125
            self.vertical_ratio = vertical_ratio_msb << 4 | vertical_ratio_lsb
            self.fractional_vertical_ratio = frac_vertical_ratio
        if self.vertical_ratio and self.fractional_vertical_ratio:
            calc_vertical_ratio = self.vertical_ratio + self.fractional_vertical_ratio
            return calc_vertical_ratio
        else:
            return None

    @lazyproperty
    def calculated_stride_length(self):
        if self.is_data_page_b:
            steplength_msb = self.msg.content[5] & 0b11111
            steplength_lsb = self.msg.content[4] 
            self.stride_length = steplength_msb << 8 | steplength_lsb
        return self.stride_length

    @lazyproperty
    def calculated_is_walking(self):
        if self.is_data_page_a:
            self.is_walking = (self.msg.content[2] & 0b00100000)>>5
        return self.is_walking

    @lazyproperty
    def calculated_stance_time(self):
        if self.is_data_page_a:
            stance_time = self.msg.content[6] & 0b1111111
            frac_stance_time_LSB = (self.msg.content[6] & 0b10000000)>>7
            frac_stance_time_MSB = (self.msg.content[7] & 0b1)

            self.stance_time = stance_time
            self.fractional_stance_time = (frac_stance_time_MSB<<1 | frac_stance_time_LSB)*0.25
        if self.stance_time and self.fractional_stance_time:
            calc_stance_time = self.stance_time+self.fractional_stance_time
            return calc_stance_time
        else:
            return None

    @lazyproperty
    def calculated_step_count(self):
        if self.is_data_page_a:
            self.step_count = (self.msg.content[7] & 0b11111110) >> 1
        return self.step_count

    @lazyproperty
    def calculated_cadence(self):
        if self.is_data_page_a:
            self.cadence = int(self.msg.content[1])
            self.fractional_cadence = (self.msg.content[2]& 0b11111)*0.03125
        if self.cadence and self.fractional_cadence:
            calc_cadence = self.cadence + self.fractional_cadence
            return calc_cadence
        else:
            return None

    @lazyproperty
    def manufacturer(self):
        if self.is_mfg_info_page:
            self.mfg_id = int(self.msg.content[5]<<8 | self.msg.content[4])
        return self.mfg_id

    @lazyproperty
    def calculated_module_orientation(self):
        if self.is_data_page_b:
            orientation = self.msg.content[5] & 0b100000 >> 5 
            self.module_orientation = 'UPSIDE_DOWN' if orientation==1 else 'RIGHT_SIDE_UP'
        return self.module_orientation

    def __str__(self):
        return super().__str__()

    def data(self):
        msg = super().json()
        msg['deviceType']='RunningDynamics'
        msg['manufacturer_id']=self.manufacturer
        msg['sensorData']={
            'module_orientation': self.calculated_module_orientation,
            'ground_contact_time': self.calculated_gct, 
            'ground_contact_balance': self.calculated_ground_contact_balance,
            'vertical_ratio': self.calculated_vertical_ratio,
            'vertical_oscillation': self.calculated_vertical_oscillation,
            'stride_length': self.calculated_stride_length,
            'run_cadence': self.calculated_cadence,
            'step_count': self.calculated_step_count,
            'stance_time': self.calculated_stance_time,
            'is_walking': self.calculated_is_walking
            }
        return msg