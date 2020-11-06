# -*- coding: utf-8 -*-
from .interface import SignalGenerator


class NF_WF1946(SignalGenerator):
    IDN_STR = (
        'NF-ELECTRONIC-INSTRUMENTS,WF1946',
        '"NF-ELECTRONIC-INSTRUMENTS,1945',
    )

    MIN_FREQ = 1e-8
    MAX_FREQ = 1.5e7

    def set_frequency(self, freq):
        assert self.MIN_FREQ <= freq <= self.MAX_FREQ
        self.write('FREQ %e', freq)

    def get_frequency(self):
        return float(self.query('FREQ?'))

    def set_amplitude(self, amp):
        self.write('VOLT %e', amp)

    def get_amplitude(self):
        return float(self.query('VOLT?'))

    def set_channel(self, ch):
        self.write('CHAN %d', ch)

    def start(self):
        self.write(':OUTP:STAT ON')

    def stop(self):
        self.write(':OUTP:STAT OFF')
