from __future__ import division
import os
import utils
import numpy
import localvlc.misc as misc
import localvlc.files as files
from utils.serializer import DillSerializer
import localvlc.performance.parameter_statistics as parameters

def get_value(keyword, data):
    for key in data:
        if keyword in key:
            return key, data[key]
    return None

def ratio(wo_glass, w_glass):
    divisor_wo = numpy.mean(wo_glass)
    if divisor_wo == 0.0:
        return 1
    else:
        divisor_w = numpy.mean(w_glass)
        return round(divisor_w / divisor_wo, 2)

def glass_ratio(statistics_subdir, filename, vlc_evaluation_w, vlc_evaluation_wo):
    data = "### Without glass\n"
    data += "throughput\n"
    data += utils.statistics.get_summary(vlc_evaluation_wo.get_throughput()) + "\n"
    data += "---\n"
    data += "error\n"
    data += utils.statistics.get_summary(vlc_evaluation_wo.get_error()) + "\n"
    data += "---\n"
    data += "### With glass\n"
    data += "throughput\n"
    data += utils.statistics.get_summary(vlc_evaluation_w.get_throughput()) + "\n"
    data += "---\n"
    data += "error\n"
    data += utils.statistics.get_summary(vlc_evaluation_w.get_error()) + "\n"
    data += "---\n"
    data += "### Ratio\n"
    data += "throughput: "
    data += str(ratio(vlc_evaluation_wo.get_throughput(), vlc_evaluation_w.get_throughput())) + "\n"
    data += "error: "
    data += str(ratio(vlc_evaluation_wo.get_error(), vlc_evaluation_w.get_error()))
    misc.log(data, statistics_subdir, filename)
    
def vlc_window_glass():
    data_directory = "vlc_window_glass/"
    result_directory = files.dir_results + data_directory
    statistics_subdir = data_directory
    min_throughput = -50
    min_error = -0.008
    max_throghput, max_error = parameters.get_max_throughput_error(result_directory)
    directed_led = dict()
    pervasive_led = dict()
    for f in os.listdir(result_directory):
        path = result_directory + f
        vlc_evaluation = DillSerializer(path).deserialize()
        if "directed" in f:
            directed_led[f] = vlc_evaluation
        elif "pervasive" in f:
            pervasive_led[f] = vlc_evaluation
    filename = ["directed_led", "pervasive_led"]
    for i, led in enumerate([directed_led, pervasive_led]):
        key_w_glass, vlc_evaluation_w = get_value("with_glass", led)
        key_wo_glass, vlc_evaluation_wo = get_value("without_glass", led)        
        parameters.throughput_error_plot(statistics_subdir, key_w_glass,
                              vlc_evaluation_w.get_throughput(),
                              vlc_evaluation_w.get_error(),
                              None,
                              min_throughput, max_throghput,
                              min_error, max_error)
        parameters.throughput_error_plot(statistics_subdir, key_wo_glass,
                              vlc_evaluation_wo.get_throughput(),
                              vlc_evaluation_wo.get_error(),
                              None,
                              min_throughput, max_throghput,
                              min_error, max_error)
        glass_ratio(statistics_subdir, "ratio_" + filename[i],
                    vlc_evaluation_w, vlc_evaluation_wo)
        
def main():
    vlc_window_glass()    
    
if __name__ == "__main__":
    main()
