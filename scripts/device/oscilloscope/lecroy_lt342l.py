# -*- coding: utf-8 -*-
import struct

import numpy as np

from .interface import Oscilloscope

# Logging
from logging import getLogger, NullHandler
logger = getLogger(__name__)
logger.addHandler(NullHandler())


CHANNEL_LABELS = ('C1','C2', 'TA', 'TB', 'TC', 'TD')

class Lecroy_LT342L(Oscilloscope):
    IDN_STR = ('*IDN LECROY,LT342L', 'LECROY,LT342L')

    def __init__(self, resource):
        super().__init__(resource)

        self.write('COMM_FORMAT DEF9,WORD,BIN')
        self.write('WAVEFORM_SETUP SP,0,NP,0,FP,0,SN,0')
        self.write('COMM_HEADER OFF')

    def start(self):
        self.write('TRIG_MODE NORM')

        for ch in CHANNEL_LABELS[-4:]:
            if self.query('%s:TRACE?', ch) == 'ON':
                self.write('%s:FUNCTION_RESET', ch)

    def stop(self):
        self.write('TRIG_MODE STOP')

    def get_data_with_ch(self, ch):
        vs = self.query_binary_values('%s:WAVEFORM? DAT1', ch,
                                      datatype='h',
                                      is_big_endian=True)
        vs = np.asarray(vs, dtype=np.float32)

        meta = self.query_binary_values('%s:WAVEFORM? DESC', ch,
                                        datatype='c')
        # Read header byte (156--160) as float
        vdiv = struct.unpack('f', b''.join(meta[156:160])[::-1])[0]
        # Read header byte (160--164) as float
        voffset = struct.unpack('f', b''.join(meta[160:164])[::-1])[0]
        # Read header byte (176--180) as float
        dt = struct.unpack('f', b''.join(meta[176:180])[::-1])[0]

        vs = vs * vdiv + voffset
        ts = np.arange(0, vs.shape[0] * dt, dt)

        return (ts, vs)

    def get_data(self):
        tdiv = self.query('TIME_DIV?')
        data = dict()
        for ch in CHANNEL_LABELS:
            if self.query('%s:TRACE?', ch) == 'OFF':
                data[ch] = np.zeros((2, 0))
            else:
                data[ch] = self.get_data_with_ch(ch)

        return data

    def query(self, cmd, *args):
        if args:
            cmd = cmd % args
        return self._inst.query(cmd)[:-1]

    def query_binary_values(self, cmd, *args, **kwargs):
        if args:
            cmd = cmd % args
        return self._inst.query_binary_values(cmd, **kwargs)
