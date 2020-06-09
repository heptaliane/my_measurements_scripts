# -*- coding: utf-8 -*-
import tkinter as tk


class Popover():
    def __init__(self, parent, text, padx=50, pady=10):
        self._parent = parent
        self.text = text
        self._window = None
        self.padx = padx
        self.pady = pady

        parent.bind('<Enter>', self.show)
        parent.bind('<Leave>', self.hide)

    def show(self, *_):
        if self._window is not None:
            return

        x, y, cx, cy = self._parent.bbox('insert')
        x = x + cx + self._parent.winfo_rootx() + self.padx
        y = y + cy + self._parent.winfo_rooty() + self.pady

        self._window = tk.Toplevel(self._parent)

        self._window.wm_overrideredirect(1)
        self._window.wm_geometry('+%d+%d' % (x, y))
        label = tk.Label(self._window, text=self.text, borderwidth=1,
                         relief=tk.SOLID, background='#ffffe0')
        label.pack(ipadx=1)

    def hide(self, *_):
        if self._window is not None:
            self._window.destroy()
            self._window = None
