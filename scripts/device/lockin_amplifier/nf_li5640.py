# -*- coding: utf-8 -*-
from enum import IntEnum
from .interface import LockinAmplifier

# Logging
from logging import getLogger, NullHandler
logger = getLogger(__name__)
logger.addHandler(NullHandler())


AVAILABLE_VOLTAGE_RANGE = (2.0e-9, 5.0e-9, 1.0e-8, 2.0e-8, 5.0e-8,
                           1.0e-7, 2.0e-7, 5.0e-7, 1.0e-6, 2.0e-6,
                           5.0e-6, 1.0e-5, 2.0e-5, 5.0e-5, 1.0e-4,
                           2.0e-4, 5.0e-4, 1.0e-3, 2.0e-3, 5.0e-3,
                           1.0e-2, 2.0e-2, 5.0e-2, 1.0e-1, 2.0e-1,
                           5.0e-1, 1.0)

# Current index 0 is not avaliable
AVAILABLE_CURRENT_RANGE = (     -1, 5.0e-15, 1.0e-14, 2.0e-14, 5.0e-14,
                           1.0e-13, 2.0e-13, 5.0e-13, 1.0e-12, 2.0e-12,
                           5.0e-12, 1.0e-11, 2.0e-11, 5.0e-11, 1.0e-10,
                           2.0e-10, 5.0e-10, 1.0e-09, 2.0e-09, 5.0e-09,
                           1.0e-08, 2.0e-08, 5.0e-08, 1.0e-07, 2.0e-07,
                           5.0e-07, 1.0e-6)


class NF_LI5640(LockinAmplifier):
    IDN_STR = 'NF-ELECTRONIC-INSTRUMENTS,LI5640'

    class OutputType(IntEnum):
        LINE = 0
        DATA1 = 1
        DATA2 = 2
        FREQUENCY = 3
        SENSITIVITY = 4
        OVERLEVEL = 5

    def __init__(self, resource):
        super().__init__(resource)

        # Enable remote control
        self.write('REN 1')

        # Set output data format: Channel1, Channel2, reference frequency
        self.set_output_type_format(self.OutputType.DATA1,
                                    self.OutputType.DATA2)

    def set_output_type_format(self, *args):
        args = [arg.value if isinstance(arg, self.OutputType) else arg
                for arg in args]
        arg_str = ','.join(['%d' % arg for arg in args])

        self.write('OTYP %s', arg_str)

    def set_variable_type(self, var_type, _=None):
        # NOTE: Channel argument is not available
        if var_type == self.VariableType.X:
            self.write('DDEF 1,0')
        elif var_type == self.VariableType.Y:
            self.write('DDEF 2,0')
        elif var_type == self.VariableType.R:
            self.write('DDEF 1,1')
        elif var_type == self.VariableType.THETA:
            self.write('DDEF 2,1')
        else:
            err_msg = 'Unexpected variable type: %s' % var_type
            logger.error(err_msg)
            raise ValueError(err_msg)

    def get_variable_type(self):
        type_tepmlate = ((self.VariableType.X, self.VariableType.R),
                         (self.VariableType.R, self.VariableType.THETA))

        var_types = [self.VariableType.UNKNOWN] * 2
        for i in range(len(var_types)):
            idx = int(self.query('DDEF? %d'), i + 1)
            if idx < 2:
                var_types[i] = type_tepmlate[i][idx]

        return tuple(var_types)

    def set_voltage_sensitivity(self, vmax):
        for i, v in enumerate(AVAILABLE_VOLTAGE_RANGE):
            if v >= vmax:
                self.write('VSEN %d', i)
                return

        # Expected voltage is out of range
        err_msg = 'Too high voltage is expected. (%.1e V > %.1e V)'
        logger.error(err_msg, vmax, AVAILABLE_VOLTAGE_RANGE[:-1])
        raise ValueError(err_msg % (vmax, AVAILABLE_VOLTAGE_RANGE[:-1]))

    def get_voltage_sensitivity(self):
        vidx = int(self.query('VSEN?'))
        return AVAILABLE_VOLTAGE_RANGE[vidx]

    def set_current_sensitivity(self, imax):
        for i, I in enumerate(AVAILABLE_CURRENT_RANGE):
            if I >= imax:
                self.write('ISEN %d', i)
                return

        # Expected current is out of range
        err_msg = 'Too high current is expected. (%.1e A > %.1e A)'
        logger.error(err_msg, imax, AVAILABLE_CURRENT_RANGE[:-1])
        raise ValueError(err_msg % (imax, AVAILABLE_CURRENT_RANGE[:-1]))

    def get_current_sensitivity(self):
        iidx = int(self.query('ISEN?'))
        return AVAILABLE_CURRENT_RANGE[iidx]

    def get_amplitude(self):
        arr = self.query('DOUT?').split(',')
        return tuple([float(v) for v in arr])

    def get_frequency(self):
        return float(self.query('FREQ?'))

    def write(self, cmd, *args):
        # Command should not end with ' '
        while cmd.endswith(' '):
            cmd = cmd[:-1]

        super().write(cmd, *args)

    def query(self, cmd, *args):
        # Command should not end with ' '
        while cmd.endswith(' '):
            cmd = cmd[:-1]

        return super().query(cmd, *args)
