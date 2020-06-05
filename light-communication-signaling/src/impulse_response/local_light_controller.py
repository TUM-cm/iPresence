import sys
import sched
import time
import numpy
import light_receiver
import paho.mqtt.client as mqtt
import utils.kernel_module as kernel_module
from utils.vlc_interfaces import ReceiverDevice
from send_light.old.led_control import LEDControl

class LocalLightController:
    
    def __init__(self, sampling_interval,
                 receiverDevice=ReceiverDevice.pd,
                 subscribe_topic="beaglebone/led",
                 publish_topic="beaglebone/light_signal",
                 period_data_threshold=5):
        self.receiverDevice = receiverDevice
        self.sampling_interval = sampling_interval
        self.subscribe_topic = subscribe_topic
        self.publish_topic = publish_topic
        self.period_data_threshold = period_data_threshold
        self.led_control = LEDControl()
        self.led_control.high_power_led_off()
        self.led_control.low_power_led_off()    
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message_period
        self.client.connect("localhost")
        self.client.loop_start()
        self.scheduler = sched.scheduler(time.time, time.sleep)
        self.scheduler_priority = 1
        
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
     
    def on_message_on_off(self, client, userdata, msg):
        if self.subscribe_topic in msg.topic and msg.payload != None:    
            if "on" in msg.payload:
                if "high" in msg.payload:
                    self.led_control.high_power_led_on()
                elif "low" in msg.payload:
                    self.led_control.low_power_led_on()
            elif "off" in msg.payload:
                if "high" in msg.payload:
                    self.led_control.high_power_led_off()
                elif "low" in msg.payload:
                    self.led_control.low_power_led_off()
    
    def start(self, callback):
        self.start = time.time()
        light_receiver.start_stream(self.receiverDevice,
                                    self.sampling_interval,
                                    callback)
    
    def callback_period(self, voltage):
        if time.time() - self.start < self.period_data_threshold:
            print numpy.mean(voltage)
        else:
            self.stop()
    
    def callback_mqtt(self, voltage):
        self.client.publish(self.publish_topic, voltage.tostring())
    
    def stop(self):
        light_receiver.stop()
        sys.exit(0)

def main():
    insert_led = kernel_module.insert("receive_light_kernel.ko", "receive_light")
    if insert_led:
        print "kernel module inserted"
        sampling_interval = 20000 # ns
        light_controller = LocalLightController(sampling_interval)
        print "start local light controller ..."
        light_controller.start(light_controller.callback_mqtt)
    
if __name__ == "__main__":
    main()
