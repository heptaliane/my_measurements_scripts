# -*- co ding: utf-8 -*-
import math
import time
from multiprocessing import Process, Queue

from device import DeviceHandler, DeviceProvider


class TimeKeeper():
    def __init__(self, interval, minrate=0.6):
        self._t0 = time.time()
        self._prev = self._t0
        self._interval = interval
        self._mintime = interval * minrate

    def __call__(self):
        t = time.time() - self._t0
        err = t - self._interval * math.floor(t / self._interval)
        return max(self._interval - err, self._mintime)


def _loop(action, interval, queue, *args, **kwargs):
    provider = DeviceProvider()
    args = [provider(v) if is_device else v for (v, is_device) in args]
    kwargs = {k:provider(v) if is_device else v
              for k, (v, is_device) in kwargs.items()}
    timer = TimeKeeper(interval)

    while True:
        time.sleep(timer())
        result = action(*args, **kwargs)
        queue.put((result, time.time()))


class Timer():
    def __init__(self, action, interval, args=list(), kwargs=dict()):
        self._action = action
        self._interval = interval
        self._process = None
        self._queue = Queue()

        self._args = [(v.address, True) if isinstance(v, DeviceHandler)
                      else (v, False) for v in args]
        self._kwargs = {k:(v.address, True) if isinstance(v, DeviceHandler)
                        else (v, False) for k, v in kwargs.items()}

    @property
    def interval(self):
        return self._interval

    @interval.setter
    def interval(self, interval):
        self.stop()
        self._interval = interval

    def stop(self):
        if self._process is not None:
            self._process.terminate()
            self._process.join()
            self._process.close()
            self._process = None

    def start(self):
        if self._process is None or not self._process.is_alive():
            self._process = Process(target=_loop, daemon=True,
                                    args=(self._action, self._interval,
                                          self._queue, *self._args),
                                    kwargs=self._kwargs)
            self._process.start()


    def join(self):
        if self._process is not None:
            self._process.join()
            self._process = None

    def fetch(self):
        return [self._queue.get() for _ in range(self._queue.qsize())]

    def __del__(self):
        self.stop()
