# -*- coding: utf-8 -*-

import tkinter as tk

from .variable import NumberVariable
from .browse_button import BrowseInput, DialogMode
from .inputs import StandardInput, MultipleInput


class GraphicalArgumentParser(object):
    def __init__(self, title='ArgumentParser'):
        self._root = tk.Tk()
        self._root.title(title)
        self._arguments = dict()
        self._components = dict()
        self._values = dict()

    def add_argument(self, name, default, type=str, nargs=1,
                     browse_mode=DialogMode.NONE, help=None):
        if not isinstance(browse_mode, DialogMode):
            browse_mode = DialogMode(browse_mode)
        self._arguments[name] = dict(value=default, argtype=type, nargs=nargs,
                                     browse_mode=browse_mode, help=help)

    def parse_args(self):
        self._create_widgets()
        self._root.mainloop()
        return self._values

    def _create_widget(self, master, *, label, value, argtype,
                       nargs, browse_mode, help):
        if argtype is int:
            value = NumberVariable(self._root, value, integer=True)
        elif argtype is float:
            value = NumberVariable(self._root, value)
        elif argtype is str:
            value = tk.StringVar(self._root, value)
        else:
            raise NotImplementedError('Unknown type: %s' % argtype)

        if browse_mode is not DialogMode.NONE:
            assert argtype is str
            return BrowseInput(master, label, value, mode=browse_mode,
                               help=help)
        elif nargs == 1:
            return StandardInput(master, label, value, help=help)
        elif isinstance(nargs, int):
            return MultipleInput(master, label, value, nargs, help=help)
        elif nargs == '+':
            return MultipleInput(master, label, value, help=help)
        else:
            raise NotImplementedError('Unknown nargs type: %s' % nargs)

    def _create_widgets(self):
        opt = dict(expand=1, fill=tk.X)
        container = tk.Frame(self._root)
        container.pack(**opt)

        for label, kwargs in self._arguments.items():
            component = self._create_widget(container, label=label, **kwargs)
            component.pack(**opt)
            self._components[label] = component

        btn_container = tk.Frame(self._root)
        btn_container.pack()

        ok_btn = tk.Button(btn_container, text='OK', command=self._on_confirm)
        ok_btn.pack(side=tk.LEFT)
        cancel_btn = tk.Button(btn_container, text='Cancel',
                               command=self._on_cancel)
        cancel_btn.pack(side=tk.LEFT)

    def _on_confirm(self):
        for lbl, component in self._components.items():
            argtype = self._arguments[lbl].get('argtype')
            self._values[lbl] = argtype(component.get())
        self._root.destroy()

    def _on_cancel(self):
        self._root.destroy()
        exit()
