import numpy
import math
import localvlc.string_similarity as string_similarity

#import functools
#from multiprocessing import Pool

# http://chriskiehl.com/article/parallelism-in-one-line/
# http://softwareramblings.com/2008/06/running-functions-as-threads-in-python.html

class VlcMetrics:
        
    def __init__(self):
        self.data_error = list()
        self.latency = list()
        self.data_period = list()
        self.throughput_ratio = list()
        self.throughput_total = list()
        self.energy_consumption = list()
    
    @staticmethod
    def convert_size(size_bytes):
        size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)
        return "%s %s" % (s, size_name[i])
    
    def get_period_scaling_factor(self, duration, time_period=1):
        period_scaling_factor = time_period / duration
        self.data_period.append(duration)
        return period_scaling_factor
    
    def throughput(self, period_scaling_factor, data):
        data = "".join(data)
        len_bytes = len(data)
        self.throughput_ratio.append(period_scaling_factor * len_bytes)
        self.throughput_total.append(len_bytes)
    
    def error(self, data, template):
        self.data_error.append(self.error_rate(data, template))
    
    def error_rate(self, results, template):
        errors = list()
        for entry in results:
            errors.append(self.get_string_error(entry, template))
        return numpy.mean(errors)
    
    def energy(self, energy):
        self.energy_consumption.append(energy)
    
    def get_string_error(self, entry, template):
        return string_similarity.jaro_winkler_similarity(entry, template)
    
    def latency(self, send_timestamp, receive_timestamp):
        self.latency.append(receive_timestamp - send_timestamp)
    
    def get_latency(self):
        return self.latency
    
    def get_data_error(self):
        return self.data_error
    
    def get_throughput_ratio(self):
        return self.throughput_ratio
    
    def get_throughput_total(self):
        return self.throughput_total
    
    def get_energy_consumption(self):
        return self.energy_consumption
    
    def get_data_period(self):
        return self.data_period
    
    def get_data_rounds(self):
        l1 = len(self.throughput_ratio)
        l2 = len(self.data_error)
        l3 = len(self.latency)
        return max(l1, l2, l3)
    
    def check_data(self):
        assert len(self.data_period) == len(self.data_error) == len(self.throughput_ratio)
    
    def print_data(self):
        print("rounds:", len(self.data_period))
        print("duration: ", self.data_period)
        print("error: ", self.data_error)
        print("throughput ratio: ", self.throughput_ratio)
        print("throughput total: ", self.throughput_total)
        print("latency: ", self.latency)
        print("energy: ", self.energy_consumption)
    