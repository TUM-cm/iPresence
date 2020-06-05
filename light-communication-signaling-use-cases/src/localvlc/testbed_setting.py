
class TestbedSetting:
    
    def __init__(self, sampling_interval, time_base_unit, name):
        self.sampling_interval = sampling_interval
        self.time_base_unit = time_base_unit
        self.name = name
    
    def get_sampling_interval(self):
        return self.sampling_interval
    
    def get_time_base_unit(self):
        return self.time_base_unit
    
    def get_name(self):
        return self.name

class Testbed:
    
    Directed_LED = TestbedSetting(50000, 130000, "directed_led") # Use for 2W, 3W, 5W
    Pervasive_LED = TestbedSetting(30000, 50000, "pervasive_led")
    Power_4W_LED = TestbedSetting(50000, 170000, "directed_led_4w")
