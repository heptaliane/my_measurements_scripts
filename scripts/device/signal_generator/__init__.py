# -*- coding: utf-8 -*-
import visa

from .interface import SignalGenerator
from .hp_8648c import HP_8648C
from .nf_wf1946 import NF_WF1946

from logging import getLogger, NullHandler
logger = getLogger(__name__)
logger.addHandler(NullHandler())


def detect_signal_generator_type(resource):
    idn = resource.query('*IDN?')

    if idn.startswith(HP_8648C.IDN_STR):
        return '8648c'
    elif idn.startswith(NF_WF1946.IDN_STR):
        return 'wf1946'

    return ''


def setup_signal_generator(address, model_id=None, resource_manager=None):
    if not isinstance(resource_manager, visa.ResourceManager):
        resource_manager = visa.ResourceManager()

    if model_id is None:
        resource = resource_manager.open_resource(address)
        model_id = detect_signal_generator_type(resource)
        assert model_id, 'Cannot detect device. (%s)' % address

    if model_id.lower() == '8648c':
        logger.info('Setup HP 8648C Signal Generator.')
        return HP_8648C(resource)

    elif model_id.lower() == 'wf1946':
        logger.info('Setup WF WF1946 Signal Generator.')
        return NF_WF1946(resource)

    raise NotImplementedError('"%s" is not implemented.' % model_id)
