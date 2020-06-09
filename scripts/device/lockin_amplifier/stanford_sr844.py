# -*- coding: utf-8 -*-
from .interface import LockinAmplifier

# Logging
from logging import getLogger, NullHandler
logger = getLogger(__name__)
logger.addHandler(NullHandler())


AVAILABLE_VOLTAGE_RANGE = (1.0e-7, 3.0e-7, 1.0e-6, 3.0e-6, 1.0e-5, 3.0e-5,
                           1.0e-4, 3.0e-4, 1.0e-3, 3.0e-3, 1.0e-2, 3.0e-2,
                           1.0e-1, 3.0e-1, 1.0)



class Stanford_SR844(LockinAmplifier):
    IDN_STR = 'Stanford_Research_Systems,SR844'

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
                self.write('SENS %d', i)
                return

        # Expected voltage is out of range
        err_msg = 'Too high voltage is expected. (%.1e V > %.1e V)'
        logger.error(err_msg, vmax, AVAILABLE_VOLTAGE_RANGE[:-1])
        raise ValueError(err_msg % (vmax, AVAILABLE_VOLTAGE_RANGE[:-1]))

    def get_voltage_sensitivity(self):
        vidx = int(self.query('SENS?'))
        return AVAILABLE_VOLTAGE_RANGE[vidx]

    def set_current_sensitivity(self, imax):
        raise NotImplementedError()

    def get_current_sensitivity(self):
        raise NotImplementedError()

    def get_amplitude(self):
        return tuple([float(self.query('OUTR? %d', i)) for i in (1, 2)])
