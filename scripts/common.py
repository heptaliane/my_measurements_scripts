# -*- coding: utf-8 -*-
import math
import numpy as np
import matplotlib.pyplot as plt

from logging import getLogger, NullHandler
logger = getLogger(__name__)
logger.addHandler(NullHandler())


def write_csv(filename, columns, labels=None, comments=None):
    csv_text = ''
    if comments is not None:
        for line in comments:
            csv_text += '# %s\n' % line
    if labels is not None:
        csv_text += '# %s\n' % '.'.join(labels)

    for i in range(len(columns[0])):
        for column in columns:
            csv_text += '%.5e, ' % column[i]
        csv_text += '\n'

    with open(filename, 'wt') as f:
        f.write(csv_text)


class CSVWriter():
    class OutputParameter():
        def __init__(self, label, fmt='%.3f', unit='', fn=None):
            self._label = label
            self._fmt = fmt
            self._unit = unit
            self._fn = fn

        @property
        def label(self):
            return self._label

        @property
        def header(self):
            if len(self._unit) > 0:
                return '%s / %s' % (self._label, self._unit)
            else:
                return self._label

        def __call__(self, value):
            if self._fn is None:
                return self._fmt % value
            else:
                return self._fmt % self._fn(value)


    def __init__(self, filename, params):
        self.filename = filename

        # Type check
        if isinstance(params, self.OutputParameter):
            params = [params]
        elif isinstance(params, (list, tuple)):
            for param in params:
                if not isinstance(param, self.OutputParameter):
                    raise ValueError('params should be OutputParameter object')
        else:
            raise ValueError('params should be OutputParameter object')

        # Generate header
        self.params = params
        with open(filename, 'w') as f:
            f.write('# %s\n' % ', '.join([p.header for p in params]))


    def __call__(self, kwargs):
        if isinstance(kwargs, dict):
            kwargs = [kwargs]

        with open(self.filename, 'a') as f:
            for row in kwargs:
                f.write('%s\n' %
                        ', '.join([p(row[p.label]) for p in self.params]))


class MeasureMonitor(object):
    def __init__(self, xlabels, ylabels):
        assert len(xlabels) == len(ylabels)

        n_rows = math.floor(math.sqrt(len(xlabels)))
        n_cols = math.ceil(math.sqrt(len(xlabels)))
        self.fig = plt.figure()
        self.axes = list()
        self.plots = list()
        for i, (xlbl, ylbl) in enumerate(zip(xlabels, ylabels)):
            self.axes.append(self.fig.add_subplot(n_rows, n_cols, i + 1))
            self.axes[i].set_xlabel(xlbl)
            self.axes[i].set_ylabel(ylbl)
            self.plots.append(self.axes[i].scatter([], []))
        plt.pause(1.0)

    def update(self, xs, ys):
        for i, (x, y) in enumerate(zip(xs, ys)):
            self.plots[i].set_offsets(np.asarray([x, y]).T)
            xmax, xmin = np.max(x), np.min(x)
            ymax, ymin = np.max(y), np.min(y)
            dx = 1 if xmax == xmin else (xmax - xmin) * 0.1
            dy = 1 if ymax == ymin else (ymax - ymin) * 0.1
            self.axes[i].set_xlim((xmin - dx, xmax + dx))
            self.axes[i].set_ylim((ymin - dy, ymax + dy))
        plt.pause(1.0)

    def finalize(self):
        plt.show()
