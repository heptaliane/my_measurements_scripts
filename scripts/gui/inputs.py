# -*- coding: utf-8 -*-

import tkinter as tk

from .popover import Popover


class StandardInput(tk.Frame):
    def __init__(self, master=None, label=None, value=None, help=None):
        super().__init__(master)
        value = tk.StringVar('') if value is None else value
        self._help = help
        self._create_widgets(label, value)

    def _create_widgets(self, label, value):
        opt = dict(side=tk.LEFT, padx=10)

        # Label
        lbl = tk.Label(self, text=label)
        lbl.pack(**opt)

        # Popover
        if self._help is not None:
            self._popover = Popover(lbl, self._help)

        # Entry
        self._input = tk.Entry(self, textvariable=value)
        self._input.pack(**opt, expand=1, fill=tk.X)

    def get(self):
        return self._input.get()


class MultipleInput(tk.Frame):
    def __init__(self, master=None, label=None, value=None, n_limit=-1,
                 help=None):
        super().__init__(master)
        self._inputs = list()
        self._default = tk.StringVar('') if value is None else value
        self._n_limit = n_limit
        self._help = help

        self._create_container()
        self._create_static_widgets(label)
        self._add_new_input()

    def _create_container(self):
        opt = dict(padx=10, side=tk.LEFT)
        self._static_container = tk.Frame(self)
        self._static_container.pack(**opt)
        self._input_container = tk.Frame(self)
        self._input_container.pack(**opt, expand=1, fill=tk.BOTH)

    def _create_static_widgets(self, label):
        # Label
        lbl = tk.Label(self._static_container, text=label)
        lbl.pack()

        # Popover
        if self._help is not None:
            self._popover = Popover(lbl, text=self._help)

        # Add / Remove input buttons
        container = tk.Frame(self._static_container)
        container.pack()
        add_btn = tk.Button(container, text='+', command=self._add_new_input)
        add_btn.pack(side=tk.LEFT)
        del_btn = tk.Button(container, text='-', command=self._del_last_input)
        del_btn.pack(side=tk.LEFT)

    def _add_new_input(self):
        if self._n_limit < 0 or len(self._inputs) < self._n_limit:
            var = type(self._default)(self, self._default.get())
            if hasattr(var, 'integer'):
                var.integer = self._default.integer
            entry = tk.Entry(self._input_container, textvariable=var)
            entry.pack(expand=1, fill=tk.X)
            self._inputs.append(entry)

    def _del_last_input(self):
        if len(self._inputs) > 1:
            inp = self._inputs.pop()
            inp.destroy()

    def get(self):
        return [inp.get() for inp in self._inputs]
