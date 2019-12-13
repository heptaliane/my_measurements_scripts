# -*- coding: utf-8 -*-
from abc import ABCMeta, abstractmethod


class DeviceHandler(metaclass=ABCMeta):
    def __init__(self, resource):
        self._inst = resource

    @abstractmethod
    def write(self, cmd, *args):
        raise NotImplementedError()

    @abstractmethod
    def query(self, cmd, *args):
        raise NotImplementedError()
