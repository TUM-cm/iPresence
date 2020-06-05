import numpy
import time
from utils.custom_enum import enum_name
import receive_light.decoding.morse_code as morse_code

class DataProvider:
    
    Mode = enum_name("raw_append_limit", "raw_append_time",
                     "raw_stream", "append_time",
                     "morse_append_time", "stream")
    
    def __init__(self, callback, data_mode, limit_data_period, limit_data_amount, max_data_points):        
        self.callback = callback
        self.start_time = None
        self.limit_data_period = limit_data_period
        self.limit_data_amount = limit_data_amount
        if data_mode == DataProvider.Mode.raw_append_limit:
            self.voltage_data = numpy.empty(max_data_points, dtype=numpy.int32)
            self.voltage_time_data = numpy.empty(max_data_points, dtype=numpy.uint32)
            self.data_callback = self.raw_data_append_limit
            self.data_index = 0        
        elif data_mode == DataProvider.Mode.raw_stream:
            self.data_callback = self.raw_data_stream        
        elif data_mode == DataProvider.Mode.stream:
            self.data_callback = self.stream
        elif data_mode == DataProvider.Mode.append_time:
            self.data_buffer = list()
            self.data_callback = self.data_append_time
        elif data_mode == DataProvider.Mode.morse_append_time:
            self.data_buffer = list()
            self.data_callback = self.morse_append_time
        elif data_mode == DataProvider.Mode.raw_append_time:
            self.voltage_buffer = list()
            self.time_buffer = list()
            self.data_callback = self.raw_append_time
    
    def raw_data_stream(self, voltage, voltage_time):
        return self.callback(voltage, voltage_time)
    
    def stream(self, data):
        return self.callback(data)
    
    def raw_data_append_limit(self, voltage, voltage_time):
        len_new_data = voltage.shape[0]
        size = self.voltage_data.shape[0]
        if self.data_index + len_new_data > size:
            if self.data_index != size:
                num_elem = size - self.data_index
                self.voltage_data[self.data_index:size] = voltage[:num_elem]
                self.voltage_time_data[self.data_index:size] = voltage_time[:num_elem]    
            return self.callback(self.voltage_data, self.voltage_time_data)
        self.voltage_data[self.data_index:self.data_index+len_new_data] = voltage
        self.voltage_time_data[self.data_index:self.data_index+len_new_data] = voltage_time
        self.data_index += len_new_data
    
    def raw_append_time(self, voltage, voltage_time):
        array_len = len(voltage)
        copy_voltage = numpy.empty(array_len, dtype=numpy.int)
        copy_voltage[:] = voltage
        copy_voltage_time = numpy.empty(array_len, dtype=numpy.uint)
        copy_voltage_time[:] = voltage_time
        self.voltage_buffer.append(copy_voltage)
        self.time_buffer.append(copy_voltage_time)
        # Append pointer, only append until buffer limit otherwise overwrites from the start
        #self.voltage_buffer.append(voltage)
        #self.time_buffer.append(voltage_time)
        duration = time.time() - self.start_time
        if duration >= self.limit_data_period:
            self.callback(duration, self.voltage_buffer, self.time_buffer)
    
    def morse_append_time(self, voltage, voltage_time):
        morse = morse_code.parse(voltage, voltage_time)
        self.data_buffer.append(morse)
        duration = time.time() - self.start_time
        if self.limit_data_amount:
            data = "".join(self.data_buffer)
            data_len = len(data)
            if data_len >= self.limit_data_amount:
                self.callback(duration, self.data_buffer)
        else:
            if duration >= self.limit_data_period:
                self.callback(duration, self.data_buffer)
    
    def data_append_time(self, data):
        self.data_buffer.append(data)
        duration = time.time() - self.start_time
        if self.limit_data_amount:
            data = "".join(self.data_buffer)
            data_len = len(data)
            if data_len >= self.limit_data_amount:
                self.callback(duration, self.data_buffer)
        else:
            if duration >= self.limit_data_amount:
                self.callback(duration, self.data_buffer)
    
    def set_start_time(self):
        self.start_time = time.time()
    
    def get_data_callback(self):
        return self.data_callback
    