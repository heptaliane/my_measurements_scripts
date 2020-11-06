#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import time

import numpy as np

from common import write_csv
from device import Oscilloscope, Multimeter
from gui import GPIBArgumentParser, DialogMode

from logging import getLogger, INFO, StreamHandler, NullHandler
root_logger = getLogger()
root_logger.addHandler(StreamHandler())
root_logger.setLevel(INFO)
logger = getLogger(__name__)
logger.addHandler(NullHandler())


def parse_arguments():
    parser = GPIBArgumentParser('Temperature trace oscilloscope monitor')
    parser.add_argument('output directory', './data/oscilloscope/',
                        browse_mode=DialogMode.DIRECTORY)
    parser.add_argument('oscilloscope cumlative time', 10.0, type=float)
    parser.add_argument('temperature measurements frequency',
                        5, type=int)
    parser.add_argument('monitor interval', 0.0, type=float)
    parser.add_argument('max monitor points', 100, type=int)
    parser.add_device('oscilloscope', Oscilloscope)
    parser.add_device('mulimeter', Multimeter)

    args = parser.parse_args()
    return args


def ruo2_thermometer(voltage):
    a = (-0.0253762943, 0.73436073, -4.6465424, -61.5460561,
         1060.90624, -5694.30536, 10787.7216)
    v = np.log(voltage * 1000)
    t = 0
    for i in range(len(a)):
        t += a[len(a) - i - 1] * v ** i
    return np.exp(t)


def main():
    args = parse_arguments()

    outdir = args['output directory']
    os.makedirs(outdir, exist_ok=True)

    osc = args['device']['oscilloscope']
    meter = args['device']['mulimeter']

    n_measure = args['temperature measurements frequency']
    wait_time = args['oscilloscope cumlative time'] / n_measure
    interval = args['monitor interval']

    meta = [
        'oscilloscope cumlative time: %.3e s' % args['oscilloscope cumlative time'],
    ]

    for i in range(args['max monitor points']):
        osc.start()

        temperatures = list()
        for _ in range(n_measure):
            temperatures.append(ruo2_thermometer(meter.get_voltage()))
            time.sleep(wait_time)
        temperatures.append(ruo2_thermometer(meter.get_voltage()))

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

        temperatures = np.asarray(temperatures)
        avg_temp = np.average(temperatures)
        var_temp = np.sqrt(np.average(temperatures ** 2) - avg_temp ** 2)
        comments = [
            *meta,
            'temperature: %.5e +/- %.3e K' % (avg_temp, var_temp),
        ]

        filename = '%03d_%.2e_oscilloscope.dat' % (i, np.average(temperatures))
        write_csv(os.path.join(outdir, filename), columns, labels, comments)
        logger.info('Data is saved to "%s".', filename)

        time.sleep(interval)


if __name__ == '__main__':
    main()
