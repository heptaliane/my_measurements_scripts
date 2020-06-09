# -*- coding: utf-8 -*-

import re
import tkinter as tk


class NumberVariable(tk.Variable):
    is_integer = re.compile('^-?\d+$')
    is_number = re.compile('^-?\d+(\.\d*)?((e|E)(\+|-)?\d+)?$')
    is_progress = re.compile('^(-?\d+(\.\d*)?(e|E))?$')

    def __init__(self, master=None, value=0.0, integer=False,
                 vmin=None, vmax=None, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        if type(value) == int or type(value) == float:
            self._value = value
        elif type(value) == str and self.is_number.match(value) is not None:
            self._value = float(value)
        else:
            raise ValueError('Initial value should be number or number str.')
        self.trace('w', self._validate)
        self.vmin = vmin
        self.vmax = vmax
        self._integer = integer
        self.set(value)

    @property
    def integer(self):
        return self._integer

    @integer.setter
    def integer(self, integer):
        self._integer = integer
        self._set_validate_value(self._value)

    def _set_validate_value(self, value):
        if self.vmin is not None and self.vmin > value:
            self.set(self._value)
        elif self.vmax is not None and self.vmax < value:
            self.set(self._value)
        else:
            if self._integer:
                value = int(value)
            self.set(value)
            self._value = value

    def _validate(self, *dummy):
        value = self.get()
        if type(value) == int or type(value) == float:
            self._set_validate_value(value)
            return
        if type(value) == str:
            if self.is_integer.match(value) is not None:
                self._set_validate_value(int(value))
            elif self.is_progress.match(value) is not None:
                # Nothing to do
                pass
            elif self.is_number.match(value) is not None:
                self._set_validate_value(float(value))
            else:
                self.set(self._value)
        else:
            self.set(self._value)
