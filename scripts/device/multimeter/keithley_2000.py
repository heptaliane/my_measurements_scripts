# -*- coding: utf-8 -*-
from .interface import Multimeter

class Keithley2000(Multimeter):
    IDN_STR = 'KEITHLEY INSTRUMENTS INC.,MODEL 2000,'

    def get_voltage(self, AC=False):
        cmd = 'measure:voltage%s' % (':AC?' if AC else '?')
        return float(self.query(cmd))

    def get_current(self, AC=False):
        cmd = 'measure:current%s' % (':AC?' if AC else '?')
        return float(self.query(cmd))

    def get_resistance(self, quad_wire=False):
        if quad_wire:
            return float(self.query('measure:fresistance?'))
        else:
            return float(self.query('measure:resistance?'))
