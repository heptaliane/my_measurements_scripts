# -*- coding: utf-8 -*-
from abc import ABCMeta, abstractmethod
from enum import Enum, auto

from ..interface import DeviceHandler


class LockinAmplifier(DeviceHandler, metaclass=ABCMeta):
    class VariableType(Enum):
        X = auto()
        Y = auto()
        R = auto()
        THETA = auto()
        UNKNOWN = auto()

    @abstractmethod
    def set_variable_type(self, var_type, channel):
        raise NotImplementedError()

    @abstractmethod
    def get_variable_type(self):
        raise NotImplementedError()

    @abstractmethod
    def set_voltage_sensitivity(self, vmax):
        raise NotImplementedError()

    @abstractmethod
    def get_voltage_sensitivity(self):
        raise NotImplementedError()

    @abstractmethod
    def set_current_sensitivity(self, imax):
        raise NotImplementedError()

    @abstractmethod
    def get_current_sensitivity(self):
        raise NotImplementedError()

    @abstractmethod
    def get_amplitude(self):
        raise NotImplementedError()
