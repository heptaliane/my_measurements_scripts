#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import time
import math

from device import LockinAmplifier, FrequencyCounter,\
                   Multimeter, TempratureController
from gui import GPIBArgumentParser, MeasureMonitor, DialogMode

from logging import getLogger, INFO, StreamHandler, NullHandler
root_logger = getLogger()
root_logger.addHandler(StreamHandler())
root_logger.setLevel(INFO)
logger = getLogger(__name__)
logger.addHandler(NullHandler())

DATA_LABELS = [
    'time / sec', 'T(A) / K', 'P(GHS) / atm', 'Frequency / Hz',
    'X / V', 'Y / V', 'R / V', 'Theta / degree',
]


def parse_arguments():
    parser = GPIBArgumentParser('Measurement monitor')
    parser.add_argument('output file', './data/monitor.dat',
                        browse_mode=DialogMode.WRITE,
                        help='Path to output file.')
    parser.add_argument('measurement interval', 5.0, type=float,
                        help='Measurement interval time')
    parser.add_device('Lock-in amplifier', LockinAmplifier)
    parser.add_device('Frequency counter', FrequencyCounter)
    parser.add_device('DC-Vol', Multimeter)
    parser.add_device('Temprature controller', TempratureController)

    args = parser.parse_args()
    return args


def setup_monitor():
    ghs_view = MeasureMonitor.MonitorParameter('Time / s', 'Pressure / atm')
    ghs_view.add_plot(key='P', value_fmt='%.5f atm')
    freq_view = MeasureMonitor.MonitorParameter('Time / s', 'Frequency / Hz')
    freq_view.add_plot(key='f', value_fmt='%.6f Hz')
    temp_view = MeasureMonitor.MonitorParameter('Time / s', 'Temperature / K')
    temp_view.add_plot(key='T', value_fmt='%.4f K')
    phase_view = MeasureMonitor.MonitorParameter('Time / s', 'Phase / deg')
    phase_view.add_plot(key='theta', value_fmt='%.1f')
    amp_view = MeasureMonitor.MonitorParameter('Time / s', 'Amplitude / mV',
                                               ymul=1.0e3)
    amp_view.add_plot(key='R', value_fmt='%.3e mV')
    return MeasureMonitor(ghs_view, temp_view, freq_view, phase_view, amp_view)


def main():
    args = parse_arguments()

    outfile = args['output file']
    with open(outfile, 'w') as f:
        f.write('# %s\n' % ', '.join(DATA_LABELS))

    wait_time = args.get('measurement interval')

    lockin = args['device']['Lock-in amplifier']
    counter = args['device']['Frequency counter']
    dcvol = args['device']['DC-Vol']
    temp = args['device']['Temprature controller']

    lockin.set_variable_type(lockin.VariableType.R)
    lockin.set_variable_type(lockin.VariableType.THETA)

    monitor = setup_monitor()
    P_mul = 1.0e6 / 101325 # MPa -> atm

    t0 = time.time()
    while True:
        f = counter.get()
        r, theta = lockin.get_amplitude()
        x = math.cos(math.radians(theta)) * r
        y = math.sin(math.radians(theta)) * r
        t = time.time() - t0
        P = dcvol.get_voltage() * P_mul
        T = temp.get_temprature()[0]

        with open(outfile, 'a') as fout:
            fout.write('%s\n' % ','.join([str(v) for v in (
                t, T, P, f, x, y, r, theta
            )]))

        monitor.update((t, P), (t, T), (t, f), (t, theta), (t, r))

        time.sleep(wait_time)


if __name__ == '__main__':
    main()
