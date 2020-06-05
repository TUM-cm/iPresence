import sched, time
import paho.mqtt.client as mqtt
from utils.custom_enum import enum_name

class LightBeacon:
    
    def __init__(self, remote_ip, topic="beaglebone/led"):
        self.client = mqtt.Client()
        self.client.connect(remote_ip)
        self.scheduler_prio = 1
        self.scheduler = sched.scheduler(time.time, time.sleep)
        self.topic = topic

    def start(self):
        self.start_time = time.time()
        self.scheduler.run()
    
    def add(self, delay, cmd):
        self.scheduler.enter(delay, self.scheduler_prio, self.__publish, (cmd,))
    
    def __publish(self, cmd):
        print "light time: ", time.time() - self.start_time
        self.client.publish(self.topic, cmd)

class LedAction():
    
    Action = enum_name("on", "off")
    
    def __init__(self, delay, device, action):        
        self.delay = delay
        self.device = device
        self.action = action
    
    def get_delay(self):
        return self.delay
    
    # low|high:<duration>|on|off
    def get_cmd(self):
        return self.device + ":" + str(self.action)
