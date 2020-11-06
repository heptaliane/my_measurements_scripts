# -*- coding: utf-8 -*-
from abc import ABCMeta, abstractmethod

from ..interface import DeviceHandler


class Multimeter(DeviceHandler, metaclass=ABCMeta):
    @abstractmethod
    def get_voltage(self):
        raise NotImplementedError()

    @abstractmethod
    def get_current(self):
        raise NotImplementedError()

    @abstractmethod
    def get_resistance(self):
        raise NotImplementedError()
