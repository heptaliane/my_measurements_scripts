# -*- coding: utf-8 -*-
import tkinter as tk

from .graphical_argument_parser import GraphicalArgumentParser
from .gpib_selection_box import GPIBSelectionContainer


class GPIBArgumentParser(GraphicalArgumentParser):
    reserved_names = ('gpib')
    def __init__(self, title='ArgumentParser', fmt='{label} ({address})'):
        super().__init__(title)
        self._gpibs = GPIBSelectionContainer(fmt=fmt)

    def add_device(self, label, device_type=None, help=None):
        self._gpibs.add(label, device_type)

    def add_argument(self, name, *nargs, **kwargs):
        assert name not in self.reserved_names
        super().add_argument(name, *nargs, **kwargs)

    def parse_args(self):
        self._gpibs.pack()
        self._create_widgets()
        self._root.mainloop()
        self._values['device'] = self._gpibs.get()
        return self._values
