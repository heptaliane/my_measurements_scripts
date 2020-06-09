# -*- coding: utf-8 -*-
import os
from enum import Enum
import tkinter as tk
import tkinter.filedialog as dialog

from .popover import Popover


class DialogMode(Enum):
    READ = 'r'
    WRITE = 'w'
    DIRECTORY = 'd'
    NONE = None


class BrowseInput(tk.Frame):
    def __init__(self, master=None, label=None, textvariable=None,
                 mode=DialogMode.READ, help=None):
        super().__init__(master)
        if isinstance(textvariable, tk.StringVar):
            self._path = textvariable
        else:
            self._path = tk.StringVar(master, textvariable)
        self._help = help
        self._mode = mode if isinstance(mode, DialogMode) else DialogMode(mode)
        self._create_widget(textvariable, label)

    def _create_widget(self, textvariable, label):
        opt = dict(side=tk.LEFT, padx=10)
        entry_opt = dict(**opt, expand=1, fill=tk.X)
        if label is not None:
            lbl = tk.Label(self, text=label)
            lbl.pack(**opt)
            if self._help is not None:
                self._popover = Popover(lbl, self._help)
        tk.Entry(self, textvariable=textvariable).pack(**entry_opt)
        tk.Button(self, text='Browse',
                  command=self._show_file_dialog).pack(**opt)

    def _show_file_dialog(self):
        dirname = os.path.dirname(self._path.get())
        dirname = dirname if os.path.exists(dirname) else './'

        if self._mode == DialogMode.READ:
            path = dialog.askopenfilename(initialdir=dirname)
        elif self._mode == DialogMode.WRITE:
            path = dialog.asksaveasfilename(initialdir=dirname)
        elif self._mode == DialogMode.DIRECTORY:
            path = dialog.askdirectory(initialdir=dirname)
        else:
            raise ValueError('Unknown dialog mode: %s' % self._mode)

        if path:
            self._path.set(path)

    def get(self):
        return self._path.get()

    def set(self, path):
        self._path.set(path)


class BrowseButton(tk.Frame):
    def __init__(self, master=None, label=None, callback=None):
        super().__init__(master)
        self._callback = callback if callable(callback) else None
        self._create_widget(textvariable, label)

    def _create_widget(self, label):
        tk.Button(self, text=label, command=self._show_file_dialog).pack()

    def _show_file_dialog(self):
        filename = dialog.askopenfilename()
        if self._callback is None:
            self._callback(filename)
