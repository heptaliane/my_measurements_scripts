#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import time

import numpy as np

from common import write_csv
from device import Oscilloscope
from gui import GPIBArgumentParser, DialogMode

from logging import getLogger, INFO, StreamHandler, NullHandler
root_logger = getLogger()
root_logger.addHandler(StreamHandler())
root_logger.setLevel(INFO)
logger = getLogger(__name__)
logger.addHandler(NullHandler())


def parse_arguments():
    parser = GPIBArgumentParser('Osilloscope monitor')
    parser.add_argument('output file', './data', browse_mode=DialogMode.WRITE,
                        help='Path to output directory.')
    parser.add_argument('cumulative time', 1.0, type=float,
                        help='Osilloscope signal cumlative time. (s)')
    parser.add_device('oscilloscope', Oscilloscope)

    args = parser.parse_args()
    return args


def main():
    args = parse_arguments()

    dst_file = args['output file']
    os.makedirs(os.path.dirname(dst_file), exist_ok=True)

    wait_time = args.get('cumulative time')

    osc = args['device']['oscilloscope']

    osc.start()

    time.sleep(wait_time)

    osc.stop()

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

    write_csv(dst_file, columns, labels)


if __name__ == '__main__':
    main()
