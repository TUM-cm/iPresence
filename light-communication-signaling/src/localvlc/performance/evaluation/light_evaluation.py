import numpy
import math
import localvlc.string_similarity as string_similarity

#import functools
#from multiprocessing import Pool

# http://chriskiehl.com/article/parallelism-in-one-line/
# http://softwareramblings.com/2008/06/running-functions-as-threads-in-python.html

class VlcEvaluation(object):
    
    def __init__(self):
        self.duration_data = list()
        self.throughput_data = list()
        self.error_data = list()
        self.latency_data = list()
    
    @staticmethod
    def convert_size(size_bytes):
        size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)
        return "%s %s" % (s, size_name[i])
    
    def get_period_factor(self, duration, time_period=1):
        period_factor = time_period / duration
        self.duration_data.append(duration)
        return period_factor
    
    def throughput(self, period_factor, data):
        data = "".join(data)
        len_bytes = len(data)
        period_bytes = period_factor * len_bytes
        self.throughput_data.append(period_bytes)
    
    def error(self, data, template):
        self.error_data.append(self.error_rate(data, template))
    
    def error_rate(self, results, template):
        errors = list()
        for entry in results:
            errors.append(self.get_string_error(entry, template))
        return numpy.mean(errors)
        # parallelized approach
        #pool = Pool()
        #error_rates = pool.map(functools.partial(string_similarity.jaro_winkler_similarity, template=template), data)
        #pool.close()
        #pool.join()
        #return numpy.mean(error_rates)
    
    def get_string_error(self, entry, template):
        return string_similarity.jaro_winkler_similarity(entry, template)
    
    def latency(self, send_timestamp, receive_timestamp):
        self.latency_data.append(receive_timestamp - send_timestamp)
    
    def get_latency(self):
        return self.latency_data
    
    def get_error(self):
        return self.error_data
    
    def get_throughput(self):
        return self.throughput_data
    
    def get_duration(self):
        return self.duration_data
    
    def get_data_rounds(self):
        l1 = len(self.throughput_data)
        l2 = len(self.error_data)
        l3 = len(self.latency_data)
        return max(l1, l2, l3)
    
    def check_data(self):
        assert len(self.duration_data) == len(self.error_data) == len(self.throughput_data)
        
    def print_data(self):
        print("rounds:", len(self.duration_data))
        print("duration: ", self.duration_data)
        print("error: ", self.error_data)
        print("throughput: ", self.throughput_data)
        print("latency: ", self.latency_data)
    