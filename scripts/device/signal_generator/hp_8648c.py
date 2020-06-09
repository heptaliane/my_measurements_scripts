# -*- coding: utf-8 -*-
from .interface import SignalGenerator


class HP_8648C(SignalGenerator):
    IDN_STR = 'Hewlett-Packard, 8648'

    def set_frequency(self, freq):
        self.write('FREQ:CW %e Hz', freq)

    def get_frequency(self):
        return float(self.query('FREQ:CW?'))

    def set_amplitude(self, amp):
        self.write('POW:AMPL %e V', amp)

    def get_amplitude(self):
        return float(self.query('POW:AMPL?'))

    def start(self):
        self.write('OUTP:STAT ON')

    def stop(self):
        self.write('OUTP:STAT OFF')

    def write(self, cmd, *args):
        if not cmd.endswith(' '):
            cmd += ' '

        super().write(cmd, *args)
