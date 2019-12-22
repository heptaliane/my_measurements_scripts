# -*- coding: utf-8 -*-
from .interface import Oscilloscope

# Logging
from logging import getLogger, NullHandler
logger = getLogger(__name__)
logger.addHandler(NullHandler())


class Yokogawa_DL9140L(Oscilloscope):
    IDN_STR = 'YOKOGAWA,701311'

    def __init__(self, resource):
        super().__init__(resource)

        # Use verbose query
        self.write(':communicate:verbose on ')
        # Use binary responce
        self.write(':waveform:format word ')
        # Use little endian
        self.write(':waveform:byteorder lsbfirst')

    def start(self):
        self.write(':start')

    def stop(self):
        self.write(':stop')

    def _get_data_with_ch(self, ch):
        bits = int(self.query(':waveform:bits?'))

        if bits == 16:
            data = self.query_binary_values(':waveform:send?',
                                            datatype='h',
                                            is_big_endian=False)
            data = np.asarray(data, dtype=np.float16)
        elif bits == 32:
            data = self.query_binary_values(':waveform:send?',
                                            datatype='i',
                                            is_big_endian=False)
            data = np.asarray(data, dtype=np.float32)
        elif bits == 64:
            data = self.query_binary_values(':waveform:send?',
                                            datatype='q',
                                            is_big_endian=False)
            data = np.asarray(data, dtype=np.float64)
        else:
            err_msg = 'Invalid waveform bits: %s' % bits
            logger.error(err_msg)
            raise ValueError(err_msg)

        offset = float(self.query(':waveform:offset?'))
        vrange = float(self.query(':waveform:range?'))
        srate = float(self.query(':waveform:srate?'))

        vs = data * (vrange / 3200) + offset
        ts = np.linspace(0, vs.shape[0] / srate, srate)
        return (ts, vs)

    def get_data(self):
        data = dict()
        for i in range(4):
            if int(self.query(':channel:display%d?', i)) != 1:
                data['ch%d' % i] = np.zeros((2, 0))
                continue

            self.write(':waveform:trace %d ', i)
            data['ch%d' % i] = self._get_data_with_ch(i)

        return data

    def write(self, cmd, *args):
        if not cmd.endswith(' '):
            cmd = cmd + ' '
        if not cmd.startswith(':'):
            cmd = ':' + cmd

        super().write(cmd, *args)

    def query(self, cmd, *args):
        if not cmd.startswith(':'):
            cmd = ':' + cmd

        res = super().query(cmd, *args)
        data = [item.split(' ') for item in res.split(';')]
        if len(data) == 1:
            return data[0][-1]
        else:
            return {item[0]:item[-1] for item in data}

    def query_binary_values(self, cmd, *args, **kwargs):
        if not cmd.startswith(':'):
            cmd = ':' + cmd

        return super().query_binary_values(cmd, *args, **kwargs)
