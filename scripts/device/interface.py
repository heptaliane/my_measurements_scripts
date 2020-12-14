# -*- coding: utf-8 -*-
from abc import ABCMeta, abstractmethod

from pyvisa import Resource


class DeviceHandler(metaclass=ABCMeta):
    def __init__(self, resource):
        assert isinstance(resource, Resource), \
            'Not a visa.resource.Resource instance.'
        self._inst = resource

    def write(self, cmd, *args):
        if args:
            cmd = cmd % args

        self._inst.write(cmd)

    def query(self, cmd, *args):
        if args:
            cmd = cmd % args

        if not cmd.endswith('?'):
            cmd += '?'
        return self._inst.query(cmd)[:-1]

    def query_binary_values(self, cmd, *args, **kwargs):
        if args:
            cmd = cmd % args

        if not cmd.endswith('?'):
            cmd += '?'

        return self._inst.query_binary_values(cmd, **kwargs)

    @property
    def address(self):
        return self._inst.resource_name
