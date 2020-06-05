import os
import numpy

class OfflineConnector:
    
    def __init__(self, callback, separate_data=True, data_directory="localvlc"):
        self.callback = callback
        self.run = True
        directory = os.path.join(data_directory, "morse_code")
        if separate_data:
            self.load_separate_data(directory)
        else:
            self.load_combined_data(directory)
    
    def load_combined_data(self, directory, page_size=2000):
        filename = "morse_code_word.npy"
        full_path = os.path.join(os.path.dirname(__file__), "..", directory, filename)
        data = numpy.load(full_path)
        self.voltage = data["voltage"][:page_size]
        self.voltage_time = data["time"][:page_size]
    
    def load_separate_data(self, directory):
        path_voltage = os.path.join(os.path.dirname(__file__), "..", directory, "voltage.npy")
        path_voltage_time = os.path.join(os.path.dirname(__file__), "..", directory, "time.npy")
        self.voltage = numpy.load(path_voltage)
        self.voltage_time = numpy.load(path_voltage_time)
    
    def start(self):
        while self.run:
            self.callback(self.voltage, self.voltage_time)
    
    def stop(self):
        self.run = False
