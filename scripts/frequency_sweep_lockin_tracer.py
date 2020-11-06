#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import time
import math

import numpy as np

from common import write_csv
from device import SignalGenerator, LockinAmplifier, FrequencyCounter
from gui import GPIBArgumentParser, MeasureMonitor, DialogMode

from logging import getLogger, INFO, StreamHandler, NullHandler
root_logger = getLogger()
root_logger.addHandler(StreamHandler())
root_logger.setLevel(INFO)
logger = getLogger(__name__)
logger.addHandler(NullHandler())


def parse_arguments():
    parser = GPIBArgumentParser('lock-in amplifier tracer')
    parser.add_argument('output file', './data/lock-in.dat',
                        browse_mode=DialogMode.WRITE,
                        help='Path to output file.')
    parser.add_argument('start frequency', 0.0, type=float,
                        help='Sweep frequency from this value. (Hz)')
    parser.add_argument('end frequency', 1.0, type=float,
                        help='Sweep frequency to this value. (Hz)')
    parser.add_argument('sample frequency', 1, type=int,
                        help='The number of sample frequencies.')
    parser.add_argument('cumulative time', 1.0, type=float,
                        help='Lock-in signal cumulative time. (s)')
    parser.add_device('Lock-in amplifier', LockinAmplifier)
    parser.add_device('Signal generator', SignalGenerator)
    parser.add_device('Frequency counter', FrequencyCounter)

    args = parser.parse_args()
    return args


def main():
    args = parse_arguments()

    outfile = args['output file']
    os.makedirs(os.path.dirname(outfile), exist_ok=True)
    with open(outfile, 'w') as f:
        f.write('# frequency / Hz, X / V, Y / V, R / V, Theta / degree\n')

    freq = np.linspace(args.get('start frequency'),
                       args.get('end frequency'),
                       args.get('sample frequency'), endpoint=True)
    wait_time = args.get('cumulative time')

    lockin = args['device']['Lock-in amplifier']
    sig_gen = args['device']['Signal generator']
    counter = args['device']['Frequency counter']

    lockin.set_variable_type(lockin.VariableType.X)
    lockin.set_variable_type(lockin.VariableType.Y)

    monitor = MeasureMonitor(('frequency', 'frequency'), ('X', 'Y'))
    xs = list()
    ys = list()

    sig_gen.set_frequency(freq[0])
    sig_gen.start()
    time.sleep(wait_time)
    for f in freq:
        logger.info('Set frequency: %.4e Hz', f)
        sig_gen.set_frequency(f)

        time.sleep(wait_time)

        x, y = lockin.get_amplitude()
        r = math.sqrt(x ** 2 + y ** 2)
        theta = math.degrees(math.atan2(y, x))

        if counter is not None:
            f = counter.get()

        with open(outfile, 'a') as fs:
            fs.write('%.6e, %.4e, %.4e, %.4e, %.2f\n' % (f, x, y, r, theta))

        # Update monitor
        xs.append(x)
        ys.append(y)
        monitor.update((freq[:len(xs)], freq[:len(ys)]), (xs, ys))
    sig_gen.stop()
    monitor.finalize()

if __name__ == '__main__':
    main()
