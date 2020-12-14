#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import math
import time
import numpy as np

from common import write_csv, CSVWriter
from device import Oscilloscope, TempratureController, SignalGenerator,\
                   LockinAmplifier, FrequencyCounter
from gui import GPIBArgumentParser, MeasureMonitor, DialogMode
from timer import Timer

from logging import getLogger, INFO, StreamHandler, NullHandler
root_logger = getLogger()
root_logger.addHandler(StreamHandler())
root_logger.setLevel(INFO)
logger = getLogger(__name__)
logger.addHandler(NullHandler())


def parse_arguments():
    parser = GPIBArgumentParser('Temperature controlled oscilloscope monitor')
    parser.add_argument('output directory', './data/test',
                        browse_mode=DialogMode.DIRECTORY)
    parser.add_argument('temperature set points', 'setpoint.txt',
                        browse_mode=DialogMode.READ,
                        help='one set point should be one row')
    parser.add_argument('oscilloscope relaxation time', 10.0, type=float)
    parser.add_argument('temperature measurements frequency', 10, type=int)
    parser.add_argument('temperature relaxation time', 120, type=float)
    parser.add_device('oscilloscope', Oscilloscope)
    parser.add_device('temperature controller', TempratureController)
    parser.add_device('signal generator', SignalGenerator)
    parser.add_device('lockin amplifier', LockinAmplifier)
    parser.add_device('frequency counter', FrequencyCounter)

    return parser.parse_args()


def load_setpt(setpt_file):
    with open(setpt_file, 'r') as f:
        lines = f.read().split('\n')
    return [float(line) for line in lines]


def get_temperature_data(temp, lockin, counter):
    f = counter.get()
    r, theta = lockin.get_amplitude()
    x = math.cos(math.radians(theta)) * r
    y = math.sin(math.radians(theta)) * r
    T = temp.get_temprature()[0]
    return dict(T=T, f=f, X=x, Y=y, R=r, theta=theta)


def get_oscilloscope_data(osc):
    osc.stop()
    data = osc.get_data()
    osc.start()

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

    return [{k: v[i] for k, v in zip(labels, columns)}
            for i in range(len(columns[0]))]


class ConbinationDataWriter():
    def __init__(self, outdir, osc_params, temp_params):
        self._temp_dir = os.path.join(outdir, 'temperature')
        self._osc_dir = os.path.join(outdir, 'oscilloscope')
        self._osc_params = osc_params
        self._temp_params = temp_params
        self._buffer = list()
        self._cnt = 0

        os.makedirs(self._temp_dir, exist_ok=True)
        os.makedirs(self._osc_dir, exist_ok=True)

    def _create_writer(self):
        filename = '%06d.dat' % self._cnt
        temp_writer = CSVWriter(os.path.join(self._temp_dir, filename),
                                self._temp_params)
        osc_writer = CSVWriter(os.path.join(self._osc_dir, filename),
                               self._osc_params)
        return (osc_writer, temp_writer)

    def __call__(self, osc_data, temp_data):
        self._buffer.extend(temp_data)

        for data, tosc in osc_data:
            tbuf = np.asarray([row[1] for row in self._buffer])
            idx = np.where(tbuf <= tosc)[0]

            osc_writer, temp_writer = self._create_writer()
            osc_writer(data)
            temp_writer([dict(time=tbuf[i], **self._buffer[i][0]) for i in idx])

            if len(self._buffer) > idx[-1] + 1:
                self._buffer = self._buffer[idx[-1] + 1:]
            else:
                self._buffer = []
            self._cnt += 1


def setup_monitor():
    temp_view = MeasureMonitor('time / s', 'Temperature / K')
    temp_view.add_plot(key='T', value_fmt='%.3f K')
    freq_view = MeasureMonitor('time / s', 'Frequency / Hz')
    freq_view.add_plot(key='f', value_fmt='%.5f Hz')
    amp_view = MeasureMonitor('time / s', 'Amplitude / mV', ymul=1.0e3)
    amp_view.add_plot(key='R', value_fmt='%.3e mV')
    phase_view = MeasureMonitor('time / s', 'Phase / deg')
    phase_view.add_plot(key='theta', value_fmt='%.2f')
    return MeasureMonitor(temp_view, freq_view, amp_view, phase_view)


class MeasurementUpdater():
    def __init__(self, outdir, osc_timer, temp_timer, osc_params, temp_params):
        # Timers
        self._osc_timer = osc_timer
        self._temp_timer = temp_timer

        # Data writers
        self.evaluator = ConbinationDataWriter(outdir, osc_params, temp_params)
        monitor_dir = os.path.join(outdir, 'monitor')
        self.monitor = ConbinationDataWriter(monitor_dir,
                                             osc_params, temp_params)
        self.logger = CSVWriter(os.path.join(monitor_dir, 'monitor.dat'),
                                temp_params)

        # GUI
        self.viewer = setup_monitor()

        self._eval = False
        self._ready = False
        self._t0 = float('nan')

    def eval(self):
        self._eval = True
        self._ready = False

    def relax(self):
        self._eval = False

    def is_eval(self):
        return self._eval

    def start(self):
        self._osc_timer.start()
        self._temp_timer.start()
        self._t0 = time.time()

    def __call__(self):
        assert not math.isnan(self._t0), 'Cannot call updater before start()'

        osc_data = [(data, t - self._t0)
                    for data, t in self._osc_timer.fetch()]
        temp_data = [(data, t - self._t0)
                     for data, t in self._temp_timer.fetch()]

        # Update logger
        data = [dict(time=t, **kwargs) for (kwargs, t) in temp_data]
        self.logger(data)

        # Update viewer
        t = [kwargs.get('t') for kwargs in data]
        self.viewer.update((t, [kwargs.get('T') for kwargs in data]),
                           (t, [kwargs.get('f') for kwargs in data]),
                           (t, [kwargs.get('R') for kwargs in data]),
                           (t, [kwargs.get('theta') for kwargs in data]))

        if self._eval and self._ready:
            self.evaluator(osc_data, temp_data)
            if len(osc_data) > 0:
                self.relax()
        else:
            if self._eval:
                self._ready = len(osc_data) > 0
            self.monitor(osc_data, temp_data)


def main():
    args = parse_arguments()

    # Load set points
    setpts = load_setpt(args['temperature set points'])

    osc = args['device']['oscilloscope']
    temp = args['device']['temperature controller']
    sig = args['device']['signal generator']
    lockin = args['device']['lockin amplifier']
    counter = args['device']['frequency counter']

    # Monitor R & theta
    lockin.set_variable_type(lockin.VariableType.R)
    lockin.set_variable_type(lockin.VariableType.THETA)

    osc_wait_time = args['oscilloscope relaxation time']
    temp_wait_time = osc_wait_time / args['temperature measurements frequency']
    relax_time = args['temperature relaxation time']
    update_time = temp_wait_time * 0.5
    assert osc_wait_time > temp_wait_time
    assert relax_time > temp_wait_time

    # Timer
    osc_timer = Timer(get_oscilloscope_data, osc_wait_time, args=(osc,))
    temp_timer = Timer(get_temperature_data, temp_wait_time,
                       args=(temp, lockin, counter))

    # Get valid oscilloscope data labels
    osc_data = get_oscilloscope_data(osc)
    osc_keys = osc_data[0].keys()
    osc.stop()

    # Output data labels
    temp_parameters = [
        CSVWriter.OutputParameter('time', fmt='%.3f', unit='s'),
        CSVWriter.OutputParameter('T', fmt='%.5f', unit='K'),
        CSVWriter.OutputParameter('f', fmt='%.5f', unit='Hz'),
        CSVWriter.OutputParameter('X', fmt='%.3e', unit='V'),
        CSVWriter.OutputParameter('Y', fmt='%.3e', unit='V'),
        CSVWriter.OutputParameter('R', fmt='%.3e', unit='V'),
        CSVWriter.OutputParameter('theta', fmt='%.2f', unit='degree'),
    ]
    osc_parameters = [CSVWriter.OutputParameter(lbl, fmt='%.6e')
                      for lbl in osc_keys]

    # Create updater
    outdir = args['output directory']
    updater = MeasurementUpdater(outdir, osc_timer, temp_timer,
                                 osc_parameters, temp_parameters)

    # Measurement loop
    sig.start()
    osc.start()
    updater.start()
    for T_next in setpts:
        temp.set_temprature(T_next)
        temp.start_control()
        T = temp.get_temprature()[0]
        logger.info('Set point: %.3f K (current: %.3f K)', T_next, T)

        # Relaxation
        t = time.time()
        updater.relax()
        while time.time() - t < relax_time:
            updater()
            time.sleep(update_time)

        # Evaluation
        logger.info('Start evaluation measurement')
        updater.eval()
        while updater.is_eval():
            updater()
            time.sleep(update_time)

    sig.stop()
    osc.stop()


if __name__ == '__main__':
    main()
