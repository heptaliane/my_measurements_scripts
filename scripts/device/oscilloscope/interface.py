# -*- coding: utf-8 -*-
from abc import ABCMeta, abstractmethod

from .. import DeviceHandler


class Oscilloscope(DeviceHandler, metaclass=ABCMeta):

    @abstractmethod
    def start(self):
        raise NotImplementedError()

    @abstractmethod
    def stop(self):
        raise NotImplementedError()

    @abstractmethod
    def get_data(self):
        raise NotImplementedError()
