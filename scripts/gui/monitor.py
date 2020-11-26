# -*- coding: utf-8 -*-
import math
import numpy as np
import matplotlib.pyplot as plt


class MeasureMonitor():
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
        plt.pause(0.1)

    def finalize(self):
        plt.show()
