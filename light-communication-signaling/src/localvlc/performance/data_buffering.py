# -*- coding: utf-8 -*- 
from __future__ import division
import os
import glob
import time
import numpy
import itertools
import matplotlib
import localvlc.misc # for plot font
import matplotlib.pyplot as plt
import coupling.utils.misc as misc
from utils.nested_dict import nested_dict
from utils.serializer import DillSerializer
import utils.kernel_module as kernel_module
import receive_light.decoding.morse_code as morse_code
from receive_light.connector_local import LocalConnector

matplotlib.rcParams['lines.linewidth'] = 3
matplotlib.rcParams['lines.markersize'] = 12

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
markers = ["o", "v", "s", "^", "*", ">", "d", "<"]

# python -m localvlc.performance.data_buffering

# Source code
# page_idx == page_size (receive_light_kernel)
# page == num_pages
# calculate_buffer (c_light_receiver)
# shared.h
#    #define MAX_BUFFER_BYTES 8257536
#    #define MAX_BUFFER_SIZE MAX_BUFFER_BYTES/(SIZE_SINGLE_BUFFER_ENTRY*NUM_BUFFER)
# user.h
#    #define NANOSECOND 1000000000 (=1s)
#    #define MAX_PER_SECOND 30000

class BufferingEvaluation:
    
    def __init__(self, sampling_rate, rounds, evaluation_type, limit_data_period):
        self.sampling_rate = sampling_rate
        self.rounds = rounds
        self.evaluation_type = evaluation_type
        self.timestamp = None
        self.durations = list()
        self.ratio_signal_payloads = list()
        self.counter = 0
        self.limit_data_period = limit_data_period
        self.morse_data = list()
        self.throughput = list()
    
    def start(self):
        self.connector = LocalConnector(self.callback, self.sampling_rate)
        self.connector.start()
    
    def callback(self, voltage, voltage_time):
        if "payload" in self.evaluation_type:
            msg = morse_code.parse(voltage, voltage_time)
            len_voltage = len(voltage)
            len_msg = len(msg)
            self.ratio_signal_payloads.append(len_msg / len_voltage)
            #print("ratio payload: {}".format(self.ratio_signal_payloads[-1] * 100))
            #print("".join(msg))
        elif "time" in self.evaluation_type:
            if self.timestamp:
                duration = time.time() - self.timestamp
                self.durations.append(duration)
                #print("duration: {}".format(duration))
            self.timestamp = time.time()
        elif "throughput" in self.evaluation_type:
            msg = morse_code.parse(voltage, voltage_time)
            self.morse_data.append(msg)
            if self.timestamp:
                duration = time.time() - self.timestamp
                if duration >= self.limit_data_period:
                    msg = "".join(self.morse_data)
                    self.morse_data = list()
                    self.timestamp = None
                    self.throughput.append(len(msg) / duration) # s
                    if self.counter == self.rounds:
                        self.connector.stop()
                    self.counter += 1
                    print("duration: ", duration)
                    print("msg len: ", len(msg))
            if not self.timestamp:
                self.timestamp = time.time()
        
        if not "throughput" in self.evaluation_type:
        #if "payload" in self.evaluation_type or "time" in self.evaluation_type:
            if self.counter == self.rounds:
                self.connector.stop()
            self.counter += 1
    
    def get_durations(self):
        return self.durations
    
    def get_num_pages(self):
        return self.connector.get_num_pages()
        
    def get_page_size(self):
        return self.connector.get_page_size()
        
    def get_ratio_signal_payloads(self):
        return self.ratio_signal_payloads
    
    def get_throughput(self):
        return self.throughput
    
def perform_evaluation(sampling_rates, evaluation_type, evaluation_rounds,
                       limit_data_period, max_page_size, datapath):
    if os.path.exists(datapath):
        evaluation_data = DillSerializer(datapath).deserialize()
    else:
        evaluation_data = nested_dict(3, dict)
    print("max page size: {}".format(max_page_size))
    for sampling_rate in sampling_rates:
        print("sampling rate: {}".format(sampling_rate))
        buffering_evaluation = BufferingEvaluation(
            sampling_rate, evaluation_rounds, evaluation_type, limit_data_period)
        print("start evaluation")
        buffering_evaluation.start() # check should be blocking until counter reaches if blocking or non blocking
        print("serialize results")
        if "payload" in evaluation_type:
            evaluation_data[max_page_size][sampling_rate] = (buffering_evaluation.get_page_size(),
                                                             buffering_evaluation.get_ratio_signal_payloads())
        elif "time" in evaluation_type:
            evaluation_data[max_page_size][sampling_rate] = (buffering_evaluation.get_page_size(),
                                                             buffering_evaluation.get_durations())
        elif "throughput" in evaluation_type:
            evaluation_data[max_page_size][sampling_rate] = (buffering_evaluation.get_page_size(),
                                                             buffering_evaluation.get_throughput())
        DillSerializer(datapath).serialize(evaluation_data)
    
def analysis_page_size_sampling_rate(datapath, ylabel):
    evaluation_data = DillSerializer(datapath).deserialize()
    max_page_sizes, sampling_rates = misc.get_all_keys(evaluation_data)
    max_page_sizes = sorted(max_page_sizes)
    sampling_rates = sorted(sampling_rates)
    plot_sampling_rates = [sampling_rate/1000 for sampling_rate in sampling_rates]
    fig, ax = plt.subplots()
    for max_page_size in max_page_sizes:
        mean = list()
        std = list()
        for sampling_rate in sampling_rates:
            result = evaluation_data[max_page_size][sampling_rate][1]
            if "payload" in ylabel.lower():
                result = [entry*100 for entry in result]
            mean.append(numpy.mean(result))
            std.append(numpy.std(result))
        ax.errorbar(plot_sampling_rates, mean, yerr=std, capsize=3, label="{:,}".format(max_page_size))
        #for x, y in zip(plot_sampling_rates, mean):
        #    ax.annotate("{0:.2f}".format(y), xy=(x*1.05, y*1.05))
    ax.set_xticks(plot_sampling_rates)
    ax.set_ylabel(ylabel)
    ax.set_xlabel(u"Sampling interval (µs)")
    ax.legend(title="Max. page size")
    ax.grid(True)
    resultpath = os.path.join(
        __location__, "..", "statistics", "buffering-algorithm", os.path.basename(datapath) + ".pdf")    
    fig.savefig(resultpath, format="pdf", bbox_inches="tight")
    plt.show()

def analysis_page_size_rounds(sampling_rate, datapath, ylabel):
    evaluation_data = DillSerializer(datapath).deserialize()
    max_page_sizes, _ = misc.get_all_keys(evaluation_data)    
    fig, ax = plt.subplots()
    print(os.path.basename(datapath))
    marker_cycle = itertools.cycle(markers)
    for max_page_size in max_page_sizes:
        result = evaluation_data[max_page_size][sampling_rate][1]
        if "payload" in ylabel.lower():
            result = [entry*100 for entry in result]
        print("max. page size: {}".format(max_page_size))
        print("mean: {0}, std: {1}".format(numpy.mean(result), numpy.std(result)))
        x = range(len(result))
        ax.plot(x, result, label="{:,}".format(max_page_size),
                marker=marker_cycle.next(), markevery=10)
    print("---")
    ax.set_ylabel(ylabel)
    ax.set_xlabel("Num. rounds")
    ax.legend(title="Max. page size", bbox_to_anchor=(0., 1.02, 1., .102),
              loc=3, ncol=3, mode="expand", borderaxespad=0.)
    fig.set_figwidth(fig.get_figwidth()*1.35)
    ax.grid(True)
    resultpath = os.path.join(
        __location__, "..", "statistics", "buffering-algorithm", os.path.basename(datapath) + ".pdf")    
    fig.savefig(resultpath, format="pdf", bbox_inches="tight")
    plt.show()

def analysis_throughput_ratio(datapath, sampling_rate):
    evaluation_data = DillSerializer(datapath).deserialize()
    throughput_10k_page_size = evaluation_data[10000][sampling_rate][1]
    throughput_30k_page_size = evaluation_data[30000][sampling_rate][1]
    ratio = 1 - (numpy.mean(throughput_10k_page_size) / numpy.mean(throughput_30k_page_size))
    print("throughput 10k page size: ", numpy.mean(throughput_10k_page_size))
    print("throughput 30k page size: ", numpy.mean(throughput_30k_page_size))
    print("ratio between 10k and 30k page size: ", ratio*100)
    
def main():
    run_evaluation = False
    sampling_rate = 30000 # best working, no error and highest throughput
    if run_evaluation:
        kernel_module.add_light_receiver()
        evaluation_rounds = 100
        limit_data_period = 10
        max_page_size = 30000 # 10000, 20000, 30000 values (pair of voltage and time)
        #sampling_rates = [5, 10, 15, 20, 25, 30, 50, 100] # microseconds
        for evaluation_type in ["throughput"]: # ["throughput"] ["response time", "payload ratio"]
            datapath = os.path.join(
                __location__, "..", "results", "buffering-algorithm", evaluation_type.replace(" ", "-"))
            print("--------------------------------------")
            print("evaluation type: ", evaluation_type)
            perform_evaluation([sampling_rate], evaluation_type, evaluation_rounds,
                               limit_data_period, max_page_size, datapath)
    else:
        print("analysis evaluation")
        datapaths = glob.glob(os.path.join(__location__, "..", "results", "buffering-algorithm", "*"))    
        for datapath in datapaths:
            filename = os.path.basename(datapath)
            if "payload" in filename:
                ylabel = "Payload ratio (%)"
            elif "response" in filename:
                ylabel = "Response time (s)"
            elif "throughput" in filename:
                ylabel = "Throughput (B/s)"
                analysis_throughput_ratio(datapath, sampling_rate)                
            #analysis_page_size_sampling_rate(datapath, ylabel)
            analysis_page_size_rounds(sampling_rate, datapath, ylabel)
    
if __name__ == "__main__":
    main()
    