# -*- coding: utf-8 -*-
from abc import ABCMeta, abstractmethod
from enum import Enum, auto

from ..interface import DeviceHandler


class FrequencyCounter(DeviceHandler):
    @abstractmethod
    def get(self):
        raise NotImplementedError
