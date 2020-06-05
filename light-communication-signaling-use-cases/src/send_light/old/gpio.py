# -*- coding: utf-8 -*-

import threading
import os
import sys
import traceback
import pdb

def except_hook(exctype, value, tb):
    traceback.print_tb(tb)
    print(repr(value))
    pdb.post_mortem(tb)

sys.excepthook = except_hook

path = os.path
pjoin = os.path.join

gpio_root = '/sys/class/gpio'
gpiopath = lambda pin: os.path.join(gpio_root, 'gpio{0}'.format(pin))
_export_lock = threading.Lock()

_pyset = set

_open = dict()
FMODE = 'w+'

IN, OUT = 'in', 'out'
LOW, HIGH = 'low', 'high'

def _write(f, v):
    f.write(str(v))
    f.flush()

def _read(f):
    f.seek(0)
    return f.read().strip()

def _verify(function):
    """decorator to ensure pin is properly set up"""
    # @functools.wraps
    def wrapped(pin, *args, **kwargs):
        pin = int(pin)
        if pin not in _open:
            ppath = gpiopath(pin)
            if not os.path.exists(ppath):
                with _export_lock:
                    with open(pjoin(gpio_root, 'export'), 'w') as f:
                        _write(f, pin)
            _open[pin] = {
                'value': open(pjoin(ppath, 'value'), FMODE),
                'direction': open(pjoin(ppath, 'direction'), FMODE),
            }
        return function(pin, *args, **kwargs)
    return wrapped

def cleanup(pin):
    if pin not in _open:
        return
    files = _open[pin]
    files['value'].close()
    files['direction'].close()
    if os.path.exists(gpiopath(pin)):
        with _export_lock:
            with open(pjoin(gpio_root, 'unexport'), 'w') as f:
                _write(f, pin)

@_verify
def setup(pin, mode, pullup=None, initial=False):
    '''Setup pin with mode IN or OUT.

    Args:
        pin (int):
        mode (str): use either gpio.OUT or gpio.IN
        pullup (None): rpio compatibility. If anything but None, raises
            value Error
        pullup (bool, optional): Initial pin value. Default is False
    '''
    if pullup is not None:
        raise ValueError("sysfs does not support pullups")

    if mode not in (IN, OUT, LOW, HIGH):
        raise ValueError(mode)
    f = _open[pin]['direction']
    _write(f, mode)
    if mode == OUT:
        if initial:
            set(pin, 1)
        else:
            set(pin, 0)

@_verify
def mode(pin):
    '''get the pin mode

    Returns:
        str: "in" or "out"
    '''
    f = _open[pin]['direction']
    return _read(f)

@_verify
def read(pin):
    '''read the pin value

    Returns:
        bool: 0 or 1
    '''
    f = _open[pin]['value']
    out = int(_read(f))
    return out

@_verify
def set(pin, value):
    '''set the pin value to 0 or 1'''
    value = int(bool(value))
    f = _open[pin]['value']
    _write(f, value)

@_verify
def input(pin):
    '''read the pin. Same as read'''
    return read(pin)

@_verify
def output(pin, value):
    '''set the pin. Same as set'''
    return set(pin, value)

def setwarnings(value):
    '''exists for rpio compatibility'''
    pass

def setmode(value):
    '''exists for rpio compatibility'''
    pass

BCM = None  # rpio compatibility
