# -*- coding: utf-8 -*-
import pyvisa as visa

from .provider import DeviceProvider
from .interface import DeviceHandler
from .lockin_amplifier import LockinAmplifier
from .signal_generator import SignalGenerator
from .oscilloscope import Oscilloscope
from .multimeter import Multimeter
from .lcr_meter import LCRMeter
from .frequency_counter import FrequencyCounter
from .temprature_controller import TempratureController


def get_devices():
    rm = visa.ResourceManager()
    provider = DeviceProvider(rm)

    address = rm.list_resources()
    return {addr:provider(addr) for addr in address}
