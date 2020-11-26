# -*- coding: utf-8 -*-
from . import TempratureController


class Cryocon_Model62(TempratureController):
    IDN_STR = 'Cryocon Model 62'

    CH_LBLS = ('A', 'B')

    def get_temprature(self):
        Ts = list()
        for ch in self.CH_LBLS:
            T = self.query(':input %s:temper?' % ch)
            try:
                Ts.append(float(T))
            except ValueError:
                Ts.append(float('nan'))

        return tuple(Ts)

    def set_temprature(self, T, target_ch=0):
        self.write(':loop 1:source CH%s' % self.CH_LBLS[target_ch])
        self.write(':loop 1:setpt %s' % T)

    def start_control(self):
        self.write(':control')

    def stop_control(self):
        self.write(':stop')
