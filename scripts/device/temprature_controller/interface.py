# -*- coding: utf-8 -*-
from abc import ABCMeta, abstractmethod

from ..interface import DeviceHandler


class TempratureController(DeviceHandler):
    @abstractmethod
    def get_temprature(self):
        raise NotImplementedError

    @abstractmethod
    def set_temprature(self, T, target_ch=0):
        raise NotImplementedError

    @abstractmethod
    def start_control(self):
        raise NotImplementedError

    @abstractmethod
    def stop_control(self):
        raise NotImplementedError
