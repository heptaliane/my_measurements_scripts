# -*- coding: utf-8 -*-
import visa

from .interface import DeviceHandler
from .lockin_amplifier import LockinAmplifier, setup_lockin_amplifier
from .signal_generator import SignalGenerator, setup_signal_generator
from .oscilloscope import Oscilloscope, setup_oscilloscope


_SETUP_FUNCTIONS = (
    setup_lockin_amplifier,
    setup_signal_generator,
    setup_oscilloscope,
)

class DeviceManager():
    def __init__(self):
        self.resource_manager = visa.ResourceManager()

    def _try_setup_device(self, address, model_id, setup_fn):
        try:
            device = setup_fn(address, model_id, self.resource_manager)
        except NotImplementedError:
            device = None
        return device

    def setup_device(self, address, model_id=None):
        for fn in _SETUP_FUNCTIONS:
            try:
                device = fn(address, model_id, self.resource_manager)
                return device
            except NotImplementedError:
                continue

        raise NotImplementedError('Unknown device (%s)' % address)

    def setup_lockin_amplifier(self, address, model_id=None):
        return setup_lockin_amplifier(address, model_id, self.resource_manager)

    def setup_signal_generator(self, address, model_id=None):
        return setup_signal_generator(address, model_id, self.resource_manager)

    def setup_oscilloscope(self, address, model_id=None):
        return setup_oscilloscope(address, model_id, self.resource_manager)
