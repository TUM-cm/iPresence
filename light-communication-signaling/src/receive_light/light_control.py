from __future__ import division
import os
import sys
import time
import numpy
import logging
import threading
import subprocess
import utils.times as times
from utils.custom_enum import enum_name
import utils.kernel_module as kernel_module
from utils.serializer import NumpySerializer
from localvlc.testbed_setting import Testbed
from receive_light.data_provider import DataProvider
import receive_light.decoding.morse_code as morse_code
from receive_light.connector_local import LocalConnector
from receive_light.connector_offline import OfflineConnector
from receive_light.connector_socket import UdpSocketConnector
from receive_light.connector_local import LocalStreamConnector
try:
    import paho.mqtt.client as mqtt
    from crypto.aes import AESCipher
    from utils.plot import RealtimePlot
    from crypto.speck_wrapper import Speck
    from receive_light.connector_mqtt import MqttConnector
    if not os.geteuid() == 0:
        sys.exit("\nOnly root can run this script\n")
except:
    pass

# make (receive light kernel module)
# make interface (c-interface to receive light)
# python -m receive_light.light_control

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

class ReceiveLightControl:
    
    Connector = enum_name("local", "localStream", "offline", "socket", "mqtt")
    Action = enum_name("parse_morse", "morse_callback",
                       "parse_manchester", "stream_raw_light_signal",
                       "data_amount_morse", "data_amount_manchester",
                       "data_amount_manchester_speck", "data_amount_manchester_aes",
                       "evaluate_morse", "evaluate_manchester",
                       "select_token", "plot_stream", "publish",
                       "serialize_raw_data", "serialize_raw_light_signal")
    
    def __init__(self, action, conn=Connector.local, sampling_interval=20000,
                 control_sender=None, max_data_points=100000,
                 evaluator=None, evaluate_period=30, evaluate_data_amount=None,
                 evaluate_template=None, evaluate_ip=None, evaluate_port=None,
                 evaluate_throughput=False, evaluate_error=False,
                 evaluate_latency=False, evaluate_home_control=False, 
                 callback_latency=None, limit_data_amount=204800,
                 callback_morse=None, mqtt_remote_ip=None, mqtt_data_format=None,
                 data_path_voltage="./voltage", data_path_time="./time"):
        
        try:
            out = subprocess.check_output("lsmod")
            if "manchester" in action:
                if "vlc" not in out:
                    sys.exit("\nopenVLC kernel module is not available\n")    
            else:
                if "receive_light_kernel" not in out:
                    sys.exit("\nkernel module to receive light is not available\n")
        except:
            pass
        
        data_mode = DataProvider.Mode.raw_stream
        self.action = action
        self.wait_until_completion = True
        self.sampling_interval = int(sampling_interval)
        if not "manchester" in action:
            kernel_module.add_light_receiver()
        if "evaluate" in action:
            self.evaluator = evaluator
            self.evaluate_template = evaluate_template
            self.evaluate_throughput = evaluate_throughput
            self.evaluate_error = evaluate_error
            self.evaluate_latency = evaluate_latency
            self.control_sender = control_sender
        if action == ReceiveLightControl.Action.select_token:
            control_callback = self.select_token
            self.wait_until_completion = False
            self.token = None
            self.token_counter = 0
            self.evaluate_home_control = evaluate_home_control
        elif action == ReceiveLightControl.Action.parse_morse:
            control_callback = self.parse_morse
            self.wait_until_completion = False
        elif action == ReceiveLightControl.Action.morse_callback:
            control_callback = self.morse_callback
            self.wait_until_completion = False
            self.callback_morse = callback_morse
        elif "data_amount" in action:
            self.data_amount = 0
            self.wait_until_completion = False
            self.limit_data_amount = limit_data_amount
            if action == ReceiveLightControl.Action.data_amount_morse:
                control_callback = self.data_amount_morse
            elif action == ReceiveLightControl.Action.data_amount_manchester:
                data_mode = DataProvider.Mode.stream
                control_callback = self.data_amount_manchester
            elif action == ReceiveLightControl.Action.data_amount_manchester_speck:
                data_mode = DataProvider.Mode.stream
                self.receive_parameters = False
                control_callback = self.data_amount_manchester_speck
            elif action == ReceiveLightControl.Action.data_amount_manchester_aes:
                data_mode = DataProvider.Mode.stream                
                self.receive_parameters = False
                control_callback = self.data_amount_manchester_aes
        elif action == ReceiveLightControl.Action.parse_manchester:
            control_callback = self.parse_manchester
            data_mode = DataProvider.Mode.stream
            self.wait_until_completion = False
        elif action == ReceiveLightControl.Action.evaluate_morse:
            if evaluate_latency:
                control_callback = self.latency
                self.wait_until_completion = False
                self.callback_latency = callback_latency
            else:
                data_mode = DataProvider.Mode.morse_append_time
                control_callback = self.evaluate
        elif action == ReceiveLightControl.Action.evaluate_manchester:   
            data_mode = DataProvider.Mode.append_time
            control_callback = self.evaluate
        elif action == ReceiveLightControl.Action.serialize_raw_data:
            control_callback = self.serialize_raw_data
            data_mode = DataProvider.Mode.raw_append_time
            self.serializer_voltage = NumpySerializer(data_path_voltage)
            self.serializer_time = NumpySerializer(data_path_time)
        elif action == ReceiveLightControl.Action.plot_stream:
            control_callback = self.plot_stream
            self.realtime_plot = RealtimePlot(self.__handle_close_fig)
        elif action == ReceiveLightControl.Action.serialize_raw_light_signal:            
            control_callback = self.serialize_raw_light_signal
            data_mode = DataProvider.Mode.append_time
            self.serializer_voltage = NumpySerializer(data_path_voltage)
        elif action == ReceiveLightControl.Action.stream_raw_light_signal:
            data_mode = DataProvider.Mode.stream
            control_callback = self.stream_raw_light_signal
        elif action == ReceiveLightControl.Action.publish:
            self.stream_data = None
            self.mqtt_client = mqtt.Client()
            self.mqtt_client.connect("localhost")
            self.mqtt_client.loop_start()
            control_callback = self.publish_stream
        self.data_provider = DataProvider(
            control_callback, data_mode, evaluate_period, evaluate_data_amount, max_data_points)
        if conn == ReceiveLightControl.Connector.offline:
            self.connector = OfflineConnector(self.data_provider.get_data_callback())
        elif conn == ReceiveLightControl.Connector.local:
            self.connector = LocalConnector(self.data_provider.get_data_callback(), self.sampling_interval)
        elif conn == ReceiveLightControl.Connector.socket:
            #self.connector = TcpSocketConnector(self.data_provider.get_data_callback(), evaluate_ip, evaluate_port)
            self.connector = UdpSocketConnector(self.data_provider.get_data_callback(), evaluate_ip, evaluate_port)
        elif conn == ReceiveLightControl.Connector.mqtt:
            self.connector = MqttConnector(mqtt_remote_ip, self.data_provider.get_data_callback(), mqtt_data_format)
        elif conn == ReceiveLightControl.Connector.localStream:
            self.connector = LocalStreamConnector(self.data_provider.get_data_callback(), self.sampling_interval)
    
    def start(self):
        if self.wait_until_completion:
            self.data_provider.set_start_time()
            self.connector.start()
        else:
            thread = threading.Thread(target=self.connector.start)
            thread.start()
    
    def evaluate(self, duration, data):
        self.connector.stop()
        if self.action == ReceiveLightControl.Action.evaluate_manchester:
            if len(data[-1]) != len(data[-2]):
                data.pop()
        elif self.action == ReceiveLightControl.Action.evaluate_morse:
            data = "".join(data).split("\n")
            if len(data[-1]) == 0:
                data.pop()
        if self.evaluate_throughput:
            period_scaling_factor = self.evaluator.get_period_scaling_factor(duration)
            self.evaluator.throughput(period_scaling_factor, data)
        if self.evaluate_error:
            self.evaluator.error(data, self.evaluate_template)
    
    def select_token(self, voltage, voltage_time):
        msg = morse_code.parse(voltage, voltage_time)
        old_token = self.token
        parts = msg.split("\n")
        most_frequent_item = max(set(parts), key=parts.count)
        if len(most_frequent_item) == 6 and most_frequent_item.isdigit() and old_token != most_frequent_item:
            logging.info(str(time.time()) + " : " + most_frequent_item)
            self.token = most_frequent_item
            if self.evaluate_home_control:
                self.token_counter += 1
                logging.info("token counter: " + str(self.token_counter))
    
    def latency(self, voltage, voltage_time):
        msg = morse_code.parse(voltage, voltage_time)
        if self.evaluate_latency and self.evaluate_template in msg:
            self.connector.stop()
            receive_timestamp = times.get_timestamp()
            self.callback_latency(receive_timestamp)
    
    def parse_morse(self, voltage, voltage_time):
        msg = morse_code.parse(voltage, voltage_time)
        print("".join(msg))
    
    def morse_callback(self, voltage, voltage_time):
        msg = morse_code.parse(voltage, voltage_time)
        return self.callback_morse("".join(msg))
    
    def data_amount_morse(self, voltage, voltage_time):
        msg = morse_code.parse(voltage, voltage_time)
        self.data_amount_manchester(msg)
    
    def data_amount_manchester(self, data):
        self.data_amount += len(data)
        if self.data_amount >= self.limit_data_amount:
            self.connector.stop()
            print(self.data_amount)
            print("stop")
    
    def get_param(self, key, params):
        for param in params:
            if key in param:
                return param.split("=")[1]
    
    def data_amount_manchester_speck(self, data):
        if self.receive_parameters:
            plain_text = self.speck.decrypt(data)
            self.data_amount_manchester(plain_text)
        else:
            print(data)
            params = data.split(";")
            self.speck = Speck(self.get_param("key", params),
                               int(self.get_param("key_size", params)),
                               int(self.get_param("block_size", params)))
            self.receive_parameters = True
    
    def data_amount_manchester_aes(self, data):
        if self.receive_parameters:
            plain_text = self.aes.decrypt(data)
            self.data_amount_manchester(plain_text)
        else:
            pwd = data.split("=", 1)[1]
            print(pwd)
            self.aes = AESCipher.keyFromPassword(pwd)
            self.receive_parameters = True
    
    def parse_manchester(self, data):
        print(data)
    
    def serialize_raw_data(self, duration, voltage, voltage_time):
        self.connector.stop()
        print(voltage_time[0])
        print(voltage_time[0].dtype)
        self.serializer_voltage.serialize(voltage)
        self.serializer_time.serialize(voltage_time)
        print("duration: ", duration)
        print("data serialized")
    
    def serialize_raw_light_signal(self, duration, voltage):
        self.connector.stop()
        self.serializer_voltage.serialize(voltage)
        print("duration: ", duration)
        print("data serialized")
    
    def stream_raw_light_signal(self, voltage):
        print(len(voltage))
        print(voltage)
    
    def plot_stream(self, voltage, _):
        self.realtime_plot.plot(voltage)
    
    def publish_stream(self, voltage, voltage_time):
        if self.stream_data == None:
            self.stream_data = numpy.empty(shape=(2, len(voltage)))
        self.stream_data[0] = voltage
        self.stream_data[1] = voltage_time
        self.mqtt_client.publish("light_signal", self.stream_data.tostring())
        #self.mqtt_client.publish("voltage", voltage.tostring())
    
    def get_token(self):
        return self.token
    
    def __handle_close_fig(self, _):
        self.connector.stop()

def test_serialize(led):
    light_control = ReceiveLightControl(ReceiveLightControl.Action.serialize_raw_data,
                                        sampling_interval=led.get_sampling_interval(),
                                        conn=ReceiveLightControl.Connector.localStream)
    light_control.start()

def test_plot_stream():
    light_control = ReceiveLightControl(ReceiveLightControl.Action.plot_stream)
    light_control.start()

def test_publish(led):
    light_control = ReceiveLightControl(ReceiveLightControl.Action.publish,
                                        sampling_interval=led.get_sampling_interval())
    light_control.start()


if __name__ == "__main__":
    led = Testbed.Pervasive_LED
    test_plot_stream()
    test_serialize(led)
    test_publish(led)
    