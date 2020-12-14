# -*- coding: utf-8 -*-
import pyvisa as visa
from . import lockin_amplifier
from . import signal_generator
from . import oscilloscope
from . import multimeter
from . import lcr_meter
from . import frequency_counter
from . import temprature_controller

from logging import getLogger, NullHandler
logger = getLogger(__name__)
logger.addHandler(NullHandler())


def _check_model_id(model, idn_str):
    idn_templates = getattr(model, 'IDN_STR')

    if isinstance(idn_templates, str):
        idn_templates = (idn_templates,)

    for template in idn_templates:
        if idn_str.startswith(template):
            return True

    return False


def _get_model_list():
    models = list()

    for module in globals().values():
        attrs = [getattr(module, attr) for attr in dir(module)]
        attrs = [attr for attr in attrs if hasattr(attr, 'IDN_STR')]
        models.extend(attrs)

    return models


class DeviceProvider():
    def __init__(self, resource_manager=None):
        if not isinstance(resource_manager, visa.ResourceManager):
            resource_manager = visa.ResourceManager()
        self._rm = resource_manager
        self._models = _get_model_list()

    def __call__(self, address):
        resource = self._rm.open_resource(address)
        try:
            idn = resource.query('*IDN?')
        except visa.VisaIOError:
            logger.warn('Device "%s" did not return "*IDN?" responce.',
                        address)
            idn = ""

        for model in self._models:
            if _check_model_id(model, idn):
                logger.info('Device "%s" is identified. (%s)',
                            address, model.__name__)
                return model(resource)

        logger.info('Unknown device "%s" is found. (%s)', address, idn)
        return resource
