# -*- coding: utf-8 -*-
import sys

import tkinter as tk
from tkinter import ttk
from visa import Resource
from collections import OrderedDict

sys.path.append('..')

import device


def _create_selection_list(devices, fmt):
    return [fmt.format(label=dev.__class__.__name__, address=addr)
            for addr, dev in devices.items()]


def _list_device_types():
    dtypes = [getattr(device, name) for name in dir(device)]
    dtypes = [dtype for dtype in dtypes if hasattr(dtype, '__bases__')]
    dtypes = [dtype for dtype in dtypes
              if device.DeviceHandler in dtype.__bases__]
    return dtypes


def _categorize_devices(devices):
    category = dict()
    dtypes = _list_device_types()
    for dtype in dtypes:
        label = dtype.__name__.lower()
        category[label] = {k:v for k, v in devices.items()
                           if isinstance(v, dtype)}

    category['Unknown'] = {k:v for k, v in devices.items()
                           if isinstance(v, Resource)}

    return category


class GPIBSelection(tk.Frame):
    def __init__(self, master, label, devices, fmt):
        super().__init__(master)
        self._devices = OrderedDict(devices)
        self._selections = _create_selection_list(self._devices, fmt)
        self._curr = tk.StringVar()
        self._create_widget(label)

    def _create_widget(self, label):
        opt = dict(side=tk.LEFT, padx=10)

        tk.Label(self, text=label).pack(**opt)

        self._cbox = ttk.Combobox(self, state='readonly',
                                  values=self._selections,
                                  textvariable=self._curr)
        if len(self._selections) > 0:
            self._cbox.set(self._selections[0])
        self._cbox.pack(**opt)

    def get(self):
        value = self._curr.get()
        idx = self._selections.index(value)
        dev = [*self._devices.values()][idx]
        return dev


class GPIBFilteredSelection(tk.Frame):
    def __init__(self, master, label, devices, fmt):
        super().__init__(master)
        self._devices = {k:OrderedDict(v) for k, v in devices.items()}
        self._selections = {k:_create_selection_list(v, fmt)
                            for k, v in devices.items()}
        self._filters = [*devices.keys()]
        self._create_widget(label)

    def _create_widget(self, label):
        opt = dict(side=tk.LEFT, padx=10)

        tk.Label(self, text=label).pack(**opt)

        self._fil_cbox = ttk.Combobox(self, state='readonly',
                                      values=self._filters,
                                      command=self.apply_filter)
        self._fil_cbox.set(self._filters[0])
        self._fil_cbox.pack(**opt)
        self._dev_cbox = ttk.Combobox(self, state='readonly')
        self.apply_filter()
        self._dev_cbox.pack(**opt)

    def apply_filter(self, *_):
        dtype = self._fil_cbox.get()
        devices = self._selections.get(dtype)
        self._dev_cbox['value'] = devices
        if len(devices) > 0:
            self._dev_cbox.set(devices[0])

    def get(self):
        dtype = self._fil_cbox.get()
        value = self._dev_cbox.get()
        idx = self._selections.index(value)
        if idx is None:
            return ''

        dev = [*self._devices[dtype].values()][idx]
        return dev


class GPIBSelectionContainer(tk.Frame):
    def __init__(self, master=None, fmt='{label} ({address})'):
        super().__init__(master)
        self._fmt = fmt
        self._devices = _categorize_devices(device.get_devices())
        self._cboxes = dict()

    def add(self, label, dtype=None):
        if dtype is None:
            cbox = GPIBFilteredSelection(self, label, self._devices, self._fmt)
        else:
            if not isinstance(dtype, str):
                dtype = dtype.__name__
            dtype = dtype.lower()
            assert dtype in self._devices.keys(),\
                   'No such device type defined (%s)' % dtype

            cbox = GPIBSelection(self, label, self._devices[dtype], self._fmt)

        cbox.pack()
        self._cboxes[label] = cbox

    def get(self):
        return {k:v.get() for k, v in self._cboxes.items()}
