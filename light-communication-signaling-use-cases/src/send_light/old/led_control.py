import gpio

class LEDControl(object):
    
    GPIO_LOW_POWER_LED_ANODE = 60
    GPIO_HIGH_POWER = 49
    
    HIGH = 1
    LOW = 0

    def control_led(self, pin, state):
        mode = gpio.OUT
        gpio.setup(pin, mode)
        gpio.set(pin, state)

    def low_power_led_on(self):
        self.control_led(self.GPIO_LOW_POWER_LED_ANODE, self.HIGH)

    def low_power_led_off(self):
        self.control_led(self.GPIO_LOW_POWER_LED_ANODE, self.LOW)

    def high_power_led_on(self):
        self.control_led(self.GPIO_HIGH_POWER, self.HIGH)
    
    def high_power_led_off(self):
        self.control_led(self.GPIO_HIGH_POWER, self.LOW)
