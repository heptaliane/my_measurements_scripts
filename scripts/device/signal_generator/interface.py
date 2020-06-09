# -*- coding: utf-8 -*-
from abc import ABCMeta, abstractmethod

from ..interface import DeviceHandler


class SignalGenerator(DeviceHandler, metaclass=ABCMeta):

    @abstractmethod
    def set_frequency(self, freq):
        raise NotImplementedError()

    @abstractmethod
    def get_frequency(self):
        raise NotImplementedError()

    @abstractmethod
    def set_amplitude(self, amp):
        raise NotImplementedError()

    @abstractmethod
    def get_amplitude(self):
        raise NotImplementedError()

    @abstractmethod
    def start(self):
        raise NotImplementedError()

    @abstractmethod
    def stop(self):
        raise NotImplementedError()
