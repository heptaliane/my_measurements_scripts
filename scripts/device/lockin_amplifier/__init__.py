# -*- coding: utf-8 -*-
from .interface import LockinAmplifier
from .nf_li5640 import NF_LI5640

from logging import getLogger, NullHandler
logger = getLogger(__name__)
logger.addHandler(NullHandler())


def detect_lockin_amplifier_type(resource):
    idn = resource.query('*IDN?')

    if idn.startswith(NF_LI5640):
        return 'li5640'

    return ''


def setup_lockin_amplifier(address, model_id=None, resource_manager=None):
    if not isinstance(resource_manager, visa.ResourceManager):
        resource_manager = visa.ResourceManager()

    if model_id is None:
        resource = resource_manager.open_resource(address)
        model_id = detect_lockin_amplifier_type(resource)
        assert model_id, 'Cannot detect device. (%s)' % address

    if model_id.lower() == 'li5640':
        logger.info('Setup NF LI5640 Lockin Amplifier.')
        return NF_LI5640(resource)

    raise NotImplementedError('"%s" is not implemented.' % model_id)
