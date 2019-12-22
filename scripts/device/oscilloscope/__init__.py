# -*- coding: utf-8 -*-
import visa

from .interface import Oscilloscope
from .lecroy_lt342l import Lecroy_LT342L
from .yokogawa_dl9140l import Yokogawa_DL9140L

from logging import getLogger, NullHandler
logger = getLogger(__name__)
logger.addHandler(NullHandler())


def detect_oscilloscope_type(resource):
    idn = resource.query('*IDN?')

    if idn.startswith(Lecroy_LT342L.IDN_STR):
        return 'lt342l'
    elif idn.startswith(Lecroy_LT342L.IDN_STR2):
        return 'lt342l'
    elif idn.startswith(Yokogawa_DL9140L.IDN_STR):
        return 'dl9140l'

    return ''


def setup_oscilloscope(address, model_id=None, resource_manager=None):
    if not isinstance(resource_manager, visa.ResourceManager):
        resource_manager = visa.ResourceManager()

    if model_id is None:
        resource = resource_manager.open_resource(address)
        model_id = detect_oscilloscope_type(resource)
        assert model_id, 'Cannot detect device. (%s)' % address

    if model_id.lower() == 'lt342l':
        logger.info('Setup Lecroy LT342L Oscilloscope.')
        return Lecroy_LT342L(resource)

    elif model_id.lower() == 'dl9140l':
        logger.info('Setup HP DL9140L Oscilloscope.')
        return Yokogawa_DL9140L(resource)

    raise NotImplementedError('"%s" is not implemented.' % model_id)
