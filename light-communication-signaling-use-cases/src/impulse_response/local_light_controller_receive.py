import time
import sched
import paho.mqtt.client as mqtt
from send_light.old.led_control import LEDControl

class LocalLightControllerReceive(object):
    
    def __init__(self):
        self.subscribe_topic = "beaglebone/led"        
        self.led_control = LEDControl()
        self.led_control.high_power_led_off()
        self.led_control.low_power_led_off()
        
        self.scheduler = sched.scheduler(time.time, time.sleep)
        self.scheduler_priority = 1     
        
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message_period
    
    def start(self):
        self.client.connect("localhost")
        self.client.loop_forever()
    
    def on_connect(self, client, userdata, flags, rc):
        client.subscribe(self.subscribe_topic)
    
    def light_peek(self, control_on, control_off, period):
        control_on()
        self.scheduler.enter(period, self.scheduler_priority, control_off, ())
        self.scheduler.run()
    
    def on_message_period(self, client, userdata, msg):
        if self.subscribe_topic in msg.topic and msg.payload != None:
            period = float(msg.payload.split(":")[1])
            if "high" in msg.payload:
                self.light_peek(self.led_control.high_power_led_on,
                                self.led_control.high_power_led_off,
                                period)
            elif "low" in msg.payload:
                self.light_peek(self.led_control.low_power_led_on,
                                self.led_control.low_power_led_off,
                                period)

def main():
    light_controller = LocalLightControllerReceive()
    light_controller.start()
    print "dead"
        
if __name__ == "__main__":
    main()
