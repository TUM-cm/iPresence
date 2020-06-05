from __future__ import division
import os
import numpy
import localvlc.misc as misc
import localvlc.files as eval_files
import matplotlib.pyplot as plt
import utils.statistics as statistics
from utils.serializer import DillSerializer

class PlotDataPoint():
    
    def __init__(self, label, marker, color, data_series):
        self.label = label
        self.marker = marker
        self.color = color
        self.data_series = data_series
    
    def get_label(self):
        return self.label
    
    def get_marker(self):
        return self.marker
    
    def get_color(self):
        return self.color
    
    def get_data_series(self):
        return self.data_series

def difference_plot(statistics_subdir, filename, data, min_data, max_data, ylabel, xlabel):
    fig, ax = plt.subplots()
    xvalues = range(1, len(data[0].get_data_series())+1)
    for entry in data:  
        plt.plot(xvalues, entry.get_data_series(), marker=entry.get_marker(),
                 label=entry.get_label(), color=entry.get_color())
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_ylim(bottom=min_data, top=max_data)
    plt.xticks(xvalues)
    plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=len(data), mode="expand", borderaxespad=0.)
    plt.grid(True, axis="y", linestyle=misc.plot_grid_linestyle)
    fig.set_figwidth(fig.get_figwidth()*1.1, forward=True)
    plt.subplots_adjust(left=0.15, right=0.99, bottom=0.15)
    misc.savefig(statistics_subdir, filename)

def print_statistics_ambient_light(data_directory, ambient_light):
    for led, ambient_light_intensities in ambient_light.items():
        output = ""
        for ambient_light, values in ambient_light_intensities.items():
            output += ambient_light + "\n"
            output += statistics.get_summary(values) + "\n"
            output += "------------------------------\n"
        filename = "ambient_light_" + led
        misc.log(output, data_directory, filename)

def get_max_throughput_error(vlc_performance, max_factor=1.1):
    max_error = -1
    max_throughput = -1
    for vlc_results in vlc_performance.values():
        for result in vlc_results.values():
            throughput = max(result.get_throughput())
            if throughput > max_throughput:
                max_throughput = throughput
            error = max(result.get_error())
            if error > max_error:
                max_error = error
    return max_error*max_factor, max_throughput*max_factor

def print_ratio(subdir, filename, data):
    low = data[0].get_data_series()
    mid = data[1].get_data_series()
    high = data[2].get_data_series()
    
    def get_statistic(data_series):
        return round(numpy.mean(data_series), 2), round(numpy.std(data_series), 2)
    
    def get_statistic_line(mean, std):
        return "mean: " + str(mean) + ", std: " + str(std)
    
    output = "low\n"
    mean, std = get_statistic(low)
    output += get_statistic_line(mean, std) + "\n"
    output += "mid\n"
    mean, std = get_statistic(mid)
    output += get_statistic_line(mean, std) + "\n" 
    output += "high\n"
    mean, std = get_statistic(high)
    output += get_statistic_line(mean, std) + "\n"
    misc.log(output, subdir, filename)

def vlc_ambient_light():
    data_directory = "vlc_ambient_light/"
    result_directory = eval_files.dir_results + data_directory
    ambient_light = dict()
    vlc_performance = dict()
    for root, _, files in os.walk(result_directory):
        for f in files:
            #for key in ["low", "mid", "high"]:
            main_key = os.path.basename(root)
            if main_key not in ambient_light:
                ambient_light[main_key] = dict()
                vlc_performance[main_key] = dict()
            for key in ["low", "mid", "high"]:
                if key in f or key.replace(" ", "_") in f:
                    path = root + "/" + f
                    if "light_intensity" in f:
                        ambient_light[main_key][key] = [item["intensity"] for item in misc.read_json(open(path))]
                    else:
                        vlc_performance[main_key][key] = DillSerializer(path).deserialize()
    
    print_statistics_ambient_light(data_directory, ambient_light)
    
    min_error = -0.03
    min_throughput = -50
    max_error, max_throughput = get_max_throughput_error(vlc_performance)
    
    for led, vlc_results in vlc_performance.items():        
        error_data = list()
        throughput_data = list()
        for key, result in vlc_results.items():
            if "high" in key:
                idx = 2
                label = "Light high"
                marker = "D"
                color = "r"
            elif "low" in key:
                idx = 0             
                label = "Light low"
                marker = "s"
                color = "g"
            elif "mid" in key:
                idx = 1         
                label = "Light medium"
                marker = "o"
                color = "b"
            error_data.insert(idx, PlotDataPoint(label, marker, color, result.get_error()))
            throughput_data.insert(idx, PlotDataPoint(label, marker, color, result.get_throughput()))
        
        difference_plot(data_directory, "throughput_" + led, throughput_data, min_throughput, max_throughput, "Throughput (B/s)", "Evaluation round")
        difference_plot(data_directory, "error_" + led, error_data, min_error, max_error, "Error rate", "Evaluation round")
        
        print_ratio(data_directory, "error_ratio_" + led, error_data)
        print_ratio(data_directory, "throughput_ratio_" + led, throughput_data)

def main():
    vlc_ambient_light()

if __name__ == "__main__":
    main()
