import numpy
import paho.mqtt.client as mqtt

class MqttConnector:
    
    FORMAT_VOLTAGE_TIME = numpy.dtype([('voltage', 'i4'), ('time', 'u4')], align=True)
    FORMAT_VOLTAGE = numpy.dtype(numpy.int, align=True)
    #FORMAT_VOLTAGE_TIME = numpy.dtype([('voltage', 'int32'), ('time', 'uint32')], align=True)
    
    def __init__(self, host, callback, data_format, port=1883, topic="beaglebone/#"):
        self.callback = callback
        self.data_format = data_format
        self.host = host
        self.port = port
        self.topic = topic
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
    
    def start(self):
        self.client.connect(self.host, self.port)
        self.client.loop_forever()
    
    def stop(self):
        self.client.disconnect()
        
    def listen(self):
        self.client.connect(self.host, self.port)
        self.client.loop_forever()
    
    def on_connect(self, client, userdata, flags, rc):
        client.subscribe(self.topic)
    
    def on_message(self, client, userdata, msg):
        if len(msg.payload) % self.data_format.itemsize == 0:
            data = numpy.fromstring(msg.payload, dtype=self.data_format)
            if len(data.shape) == 1:
                self.callback(data)
            else:
                self.callback(data["voltage"], data["time"])
