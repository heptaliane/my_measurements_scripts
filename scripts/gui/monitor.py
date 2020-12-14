# -*- coding: utf-8 -*-
import math
from functools import reduce
import numpy as np
import matplotlib.pyplot as plt


class _PlotManager():
    def __init__(self, ax, *, key, color, line, marker,
                 maxlen, reset_on_update, text_pos, value_fmt):
        self._line = line
        if key is None:
            self._text_fmt = value_fmt
        else:
            self._text_fmt = '%s: %s' % (key, value_fmt)
        self.reset_on_update = reset_on_update
        self.maxlen = maxlen
        self._xs = list()
        self._ys = list()

        if line:
            self.plot, = ax.plot(self._xs, self._ys,
                                 label=key, color=color, marker=marker)
        else:
            self.plot = ax.scatter(self._xs, self._ys,
                                   label=key, color=color, marker=marker)
        if text_pos is None:
            self.text = None
        else:
            self.text = ax.text(*text_pos, self._text_fmt % float('nan'),
                                horizontalalignment='right',
                                color='gray',
                                transform=ax.transAxes)

    @property
    def xlim(self):
        return min(self._xs), max(self._xs)

    @property
    def ylim(self):
        return min(self._ys), max(self._ys)

    def __call__(self, xs, ys):
        if xs.shape[0] == 0 or ys.shape[0] == 0:
            return

        data = list()
        for s1, s2 in zip((self._xs, self._ys), (xs, ys)):
            if self.reset_on_update:
                data.append(s2)
            else:
                s = np.concatenate([s1, s2])
                if self.maxlen is not None:
                    s = s[-self.maxlen:]
                data.append(s)
        self._xs, self._ys = data[0], data[1]

        if self._line:
            self.plot.set_data(self._xs, self._ys)
        else:
            self.plot.set_offsets(np.asarray([self._xs, self._ys]).T)

        if self.text is not None:
            self.text.set_text(self._text_fmt % self._ys[-1])


class MeasureMonitor():
    class MonitorParameter():
        def __init__(self, xlabel=None, ylabel=None, xmul=1.0, ymul=1.0):
            self.xlabel = xlabel
            self.ylabel = ylabel
            self._xmul = xmul
            self._ymul = ymul
            self._plot_params = list()
            self._n_text = 0

        def add_plot(self, key=None, color=None, line=False, marker='o',
                     maxlen=None, reset_on_update=False,
                     value_fmt=None):
            if value_fmt is None:
                text_pos = None
            else:
                text_pos = (0.9, 1.0 - (self._n_text + 1) * 0.05)
                self._n_text += 1

            self._plot_params.append({
                'key': key,
                'color': color,
                'line': line,
                'marker': marker,
                'maxlen': maxlen,
                'reset_on_update': reset_on_update,
                'text_pos': text_pos,
                'value_fmt': value_fmt,
            })

        def create_plotter(self, ax):
            return [_PlotManager(ax, **params) for params in self._plot_params]

        def arange(self, xs, ys):
            data = list()
            for vs, mul in zip((xs, ys), (self._xmul, self._ymul)):
                if isinstance(vs, (int, float)):
                    vs = np.asarray([vs])
                if isinstance(vs, (list, tuple)):
                    vs = np.asarray(vs)
                data.append(vs * mul)
            return tuple(data)

    def __init__(self, *parameters):
        self._params = list()
        for param in parameters:
            if isinstance(param, self.MonitorParameter):
                self._params.append(param)
            else:
                raise ValueError

        n_rows = math.floor(math.sqrt(len(self._params)))
        n_cols = math.ceil(math.sqrt(len(self._params)))
        self.fig = plt.figure()
        self.axes = list()
        self._plotters = list()
        for i, param in enumerate(self._params):
            self.axes.append(self.fig.add_subplot(n_rows, n_cols, i + 1))
            self.axes[i].set_xlabel(param.xlabel)
            self.axes[i].set_ylabel(param.ylabel)
            self._plotters.append(param.create_plotter(self.axes[i]))
            if len(self._plotters[-1]) > 1:
                self.axes[i].legend(loc='lower left')
        plt.pause(1.0)

    def _fold_lims(self, lims):
        return reduce(lambda acm, lim: (min(acm[0], lim[0]),
                                        max(acm[1], lim[1])),
                      lims, (float('inf'), -float('inf')))

    def update(self, *args):
        assert len(args) == len(self._params)

        for i, data in enumerate(args):
            if data is None:
                continue
            if isinstance(data[0], (int, float)):
                data = [data]
            for plotter, coords in zip(self._plotters[i], data):
                if coords is not None:
                    plotter(*self._params[i].arange(*coords))

            xmin, xmax = self._fold_lims([p.xlim for p in self._plotters[i]])
            ymin, ymax = self._fold_lims([p.ylim for p in self._plotters[i]])
            dx = 1 if xmax == xmin else (xmax - xmin) * 0.1
            dy = 1 if ymax == ymin else (ymax - ymin) * 0.2
            self.axes[i].set_xlim((xmin - dx, xmax + dx))
            self.axes[i].set_ylim((ymin - dy, ymax + dy))

        plt.pause(0.1)

    def finalize(self):
        plt.show()
