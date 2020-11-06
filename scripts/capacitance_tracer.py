#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import time

from device import LCRMeter
from gui import GPIBArgumentParser, MeasureMonitor, DialogMode

from logging import getLogger, INFO, StreamHandler, NullHandler
root_logger = getLogger()
root_logger.addHandler(StreamHandler())
root_logger.setLevel(INFO)
logger = getLogger(__name__)
logger.addHandler(NullHandler())


def parse_arguments():
    parser = GPIBArgumentParser('Capacitance tracer')
    parser.add_argument('output file', './data/capacitance.dat',
                        browse_mode=DialogMode.WRITE,
                        help='Path to output file.')
    parser.add_argument('interval', 1.0, type=float,
                        help='Measurement interval')
    parser.add_device('LCR meter', LCRMeter)

    args = parser.parse_args()
    return args


def main():
    args = parse_arguments()

    outfile = args['output file']
    os.makedirs(os.path.dirname(outfile), exist_ok=True)
    with open(outfile, 'w') as f:
        f.write('# Time / s, capacitance / pF')

    lcr = args['device']['LCR meter']
    lcr.set_mode(lcr.Mode.CAPACITANCE, is_big_value=False)

    monitor = MeasureMonitor(('Time / s',), ('Capacitance / pF',))
    ts = list()
    cs = list()

    t0 = time.time()
    c_mul = 1.0e12
    while True:
        time.sleep(args['interval'])
        t = time.time() - t0
        c = lcr.get() * c_mul

        with open(outfile, 'a') as f:
            f.write('%.1f, %.8e\n' % (t0, c))

        ts.append(t)
        cs.append(c)
        monitor.update((ts,), (cs,))


if __name__ == '__main__':
    main()
