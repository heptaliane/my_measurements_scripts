# -*- coding: utf-8 -*-
from .interface import FrequencyCounter

class Pendulum_CNT90(FrequencyCounter):
    IDN_STR = 'PENDULUM, CNT-9'

    def get(self):
        return float(self.query(':calculate:data?'))
