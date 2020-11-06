#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import time

import numpy as np

from common import write_csv
from device import Oscilloscope, SignalGenerator
from gui import GPIBArgumentParser, DialogMode

from logging import getLogger, INFO, StreamHandler, NullHandler
root_logger = getLogger()
root_logger.addHandler(StreamHandler())
root_logger.setLevel(INFO)
logger = getLogger(__name__)
logger.addHandler(NullHandler())


def parse_arguments():
    parser = GPIBArgumentParser('Frequency sweep Oscilloscope monitor')
    parser.add_argument('output directory', './data/oscilloscope',
                        browse_mode=DialogMode.DIRECTORY,
                        help='Path to output directory.')
    parser.add_argument('start frequency', 0.0, type=float,
                        help='Sweep frequency from this value. (Hz)')
    parser.add_argument('end frequency', 1.0, type=float,
                        help='Sweep frequency to this value. (Hz)')
    parser.add_argument('sample frequency', 1, type=int,
                        help='The number of sample frequencies.')
    parser.add_argument('cumulative time', 1.0, type=float,
                        help='Oscilloscope signal cumlative time. (s)')
    parser.add_device('oscilloscope', Oscilloscope)
    parser.add_device('signal generator', SignalGenerator)

    args = parser.parse_args()
    return args


def main():
    args = parse_arguments()

    dst_dir = args['output directory']
    os.makedirs(dst_dir, exist_ok=True)

    osc = args['device']['oscilloscope']
    sig = args['device']['signal generator']

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

        filename = 'osciiloscope_monitor_%.5e_Hz.dat' % f
        write_csv(os.path.join(dst_dir, filename), columns, labels, comments)


if __name__ == '__main__':
    main()
