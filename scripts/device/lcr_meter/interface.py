# -*- coding: utf-8 -*-
from abc import ABCMeta, abstractmethod
from enum import Enum, auto

from ..interface import DeviceHandler


class LCRMeter(DeviceHandler):
    class Mode(Enum):
        CAPACITANCE = 'c'
        INDUCTANCE = 'l'
        RESISTANCE = 'r'

    @abstractmethod
    def set_mode(self, mode, is_big_value=False):
        raise NotImplementedError

    @abstractmethod
    def get(self):
        raise NotImplementedError
