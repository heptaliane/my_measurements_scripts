# -*- coding: utf-8 -*-
from .interface import LCRMeter

# Logging
from logging import getLogger, NullHandler
logger = getLogger(__name__)
logger.addHandler(NullHandler())


class HP_4284A(LCRMeter):
    IDN_STR = 'HEWLETT-PACKARD,4284A'

    def set_mode(self, mode, is_big_value=False):
        if type(mode) == str:
            mode = self.Mode(mode.lower())

        if mode == self.Mode.CAPACITANCE:
            mode_str = 'CSD' if is_big_value else 'CPD'
        elif mode == self.Mode.INDUCTANCE:
            mode_str = 'LPD' if is_big_value else 'LSD'
        elif mode == self.Mode.RESISTANCE:
            mode_str = 'CPRP' if is_big_value else 'LSRS'
        else:
            raise ValueError

        self.write(':function:impedance:type %s' % mode_str)

    def get(self):
        mode = self.query(':function:impedance:type?')
        data = self.query(':fetch?').split(',')[:2]

        # Use first parameter
        if mode[:3] in ('CSD', 'CPD', 'LPD', 'LSD'):
            return float(data[0])
        # Use second parameter
        else:
            return float(data[1])
