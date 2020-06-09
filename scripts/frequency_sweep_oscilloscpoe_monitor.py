#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import time

import numpy as np

from common import write_csv
from device import get_devices
from gui import GraphicalArgumentParser

from logging import getLogger, INFO, StreamHandler, NullHandler
root_logger = getLogger()
root_logger.addHandler(StreamHandler())
root_logger.setLevel(INFO)
logger = getLogger(__name__)
logger.addHandler(NullHandler())


def parse_arguments():
    parser = GraphicalArgumentParser('Osilloscope monitor')
    parser.add_argument('output directory', './data', browse_mode='d',
                        help='Path to output directory.')
    parser.add_argument('oscilloscope GPIB', 'GPIB0::0::INSTR',
                        help='Oscilloscope GPIB address.')
    parser.add_argument('signal generator GPIB', 'GPIB0::0::INSTR',
                        help='Signal Generator GPIB address.')
    parser.add_argument('start frequency', 0.0, type=float,
                        help='Sweep frequency from this value. (Hz)')
    parser.add_argument('end frequency', 1.0, type=float,
                        help='Sweep frequency to this value. (Hz)')
    parser.add_argument('sample frequency', 1, type=int,
                        help='The number of sample frequencies.')
    parser.add_argument('cumulative time', 1.0, type=float,
                        help='Osilloscope signal cumlative time. (s)')

    args = parser.parse_args()
    return args


def main():
    args = parse_arguments()

    dst_dir = args['output directory']
    os.makedirs(dst_dir, exist_ok=True)

    dm = DeviceManager()

    osc = dm.setup_oscilloscope(args.get('oscilloscope GPIB'))
    sig = dm.setup_signal_generator(args.get('signal generator GPIB'))

    freq = np.linspace(args.get('start frequency'),
                       args.get('end frequency'),
                       args.get('sample frequency'), endpoint=True)
    wait_time = args.get('cumulative time')

    for f in freq:
        logger.info('Set frequency: %.4e Hz' % f)
        sig.set_frequency(f)
        sig.start()
        osc.start()

        time.sleep(wait_time)

        osc.stop()
        sig.stop()

        data = osc.get_data()

        labels = list()
        columns = list()
        for label, v in data.items():
            if v[0].shape[0] == 0:
                continue
            if 'time' not in labels:
                labels.append('time')
                columns.append(v[0])
            labels.append(label)
            columns.append(v[1])
        comments = ('Frequency: %.4e Hz' % f,
                    'Cumulative time: %.2f s' % wait_time)

        filename = 'osciiloscope_monitor_%.2e_Hz.dat' % f
        write_csv(os.path.join(dst_dir, filename), columns, labels, comments)


if __name__ == '__main__':
    main()
