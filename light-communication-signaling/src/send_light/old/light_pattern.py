import time

from led_control import LEDControl
from led_control_netlink import LEDControlNetlink
from led_control_netlink import Command

HALF_SECOND = 500000000

class LightPatternsNetlink(object):
    
    def __init__(self, on=HALF_SECOND, off=HALF_SECOND):
        self.led_control = LEDControlNetlink()        
        self.high_power_start_cmd = Command("start", "high", on, off)
        self.high_power_stop_cmd = Command("stop", "high")        
        self.low_power_start_cmd = Command("start", "low", on, off)
        self.low_power_stop_cmd = Command("start", "low")
    
    def high_power_start(self):
        self.led_control.execute(self.high_power_start_cmd)
        
    def high_power_stop(self):
        self.led_control.execute(self.high_power_stop_cmd)
    
    def low_power_start(self):
        self.led_control.execute(self.low_power_start_cmd)
        
    def low_power_stop(self):
        self.led_control.execute(self.low_power_stop_cmd)

class LightPatterns(object):
    
    def __init__(self, time_delay=.100):
        self.led_control = LEDControl()        
        self.time_delay = time_delay
        self.patterns = []
        self.patterns.append(("high power", self.high_power))
        self.patterns.append(("low power", self.low_power))
        self.idx_desc = 0
        self.idx_func = 1
    
    def low_power(self):
        self.led_control.low_power_led_on()
        time.sleep(self.time_delay)
        self.led_control.low_power_led_off()
        time.sleep(self.time_delay)
    
    def high_power(self):
        self.led_control.high_power_led_on()
        time.sleep(self.time_delay)
        self.led_control.high_power_led_off()
        time.sleep(self.time_delay)