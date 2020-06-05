import ctypes
import os

class LEDControlNetlink(object):
    
    PROGRAM = 'control_led_user'
    
    def __init__(self):
        basepath = os.path.dirname(__file__)
        f = os.path.abspath(os.path.join(basepath, self.PROGRAM))
        self.control_led = ctypes.cdll.LoadLibrary(f)
        self.control_led.send_command.argtypes = [ctypes.c_char_p]
        
    def execute(self, command):
        args = ctypes.c_char_p(command.get_str())
        self.control_led.send_command(args)

class Command(object):
    
    SEPARATOR = ";"
    ACTION = "ACTION="
    DEVICE = "DEVICE="
    ON = "ON="
    OFF = "OFF="
    
    def __init__(self, action, device, on=0, off=0):
        self.action = action;
        self.device = device
        self.on = str(on)
        self.off = str(off)
        
    def get_str(self):
        return self.ACTION + self.action + self.SEPARATOR + \
            self.DEVICE + self.device + self.SEPARATOR + \
            self.ON + self.on + self.SEPARATOR + \
            self.OFF + self.off + self.SEPARATOR
