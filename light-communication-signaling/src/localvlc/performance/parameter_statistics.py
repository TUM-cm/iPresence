# -*- coding: utf-8 -*-
import os
import glob
import numpy
import localvlc.misc as misc
import localvlc.files as files
import matplotlib.pyplot as plt
import utils.statistics as statistics
from utils.serializer import DillSerializer

def throughput_error_plot(statistics_subdir, filename, throughput, error, duration,
                          min_throughput, max_throughput, min_error, max_error):
    _, ax1 = plt.subplots()
    ax2 = ax1.twinx()
    xvalues = range(1, len(error)+1)
    throughput = numpy.nan_to_num(throughput)
    error = numpy.nan_to_num(error)
    if duration and duration[0] < 3:
        error = [err*dur*10 for err, dur in zip(error, duration)]
    p1, = ax1.plot(xvalues, throughput, marker="D", label="Throughput", color="b")    
    p2, = ax2.plot(xvalues, error, marker="s", label="Error rate", color="r")
    ax1.set_xlabel("Evaluation round")
    ax1.set_ylabel("Throughput (B/s)", color=p1.get_color())
    ax2.set_ylabel("Error rate", color=p2.get_color())
    ax1.tick_params(axis='y', colors=p1.get_color())
    ax2.tick_params(axis='y', colors=p2.get_color())
    plt.xticks(xvalues)
    ax1.set_ylim(bottom=min_throughput, top=max_throughput)
    ax2.set_ylim(bottom=min_error, top=max_error)
    lines = [p1] + [p2]
    labels = [l.get_label() for l in lines]
    plt.legend(lines, labels, bbox_to_anchor=(0., 1.02, 1., .102), loc="lower left",
               ncol=2, mode="expand", borderaxespad=0.)
    plt.grid(True, axis="y", linestyle=misc.plot_grid_linestyle)
    plt.tight_layout(rect=[0, 0, 1.05, .95])
    misc.savefig(statistics_subdir, filename)

def throughput_error_statistics(filename, throughput, error):
    result = filename + "\n"
    result += "\n### Throughput ###\n"
    result += statistics.get_summary(throughput)
    result += "\n### Error rate ###\n"
    result += statistics.get_summary(error)
    return result

def find_best_vlc_parameters(result_directory, keyword, stop_keyword="light_intensity"):
    max_throughput = -1
    parameters = None
    throughput_values = None
    for f in os.listdir(result_directory):
        path = result_directory + f
        if keyword in path and stop_keyword not in path:
            vlc_evaluation = DillSerializer(path).deserialize()
            if numpy.sum(vlc_evaluation.get_error()) == 0:
                throughput = numpy.mean(vlc_evaluation.get_throughput())
                if throughput > max_throughput:
                    max_throughput = throughput
                    throughput_values = vlc_evaluation.get_throughput()
                    parameters = f
    return parameters, throughput_values

def find_max_throughput_error(result_directory):
    throughput = []
    error = []
    for f in os.listdir(result_directory):
        if "light_intensity" not in f:
            path = result_directory + f
            vlc_evaluation = DillSerializer(path).deserialize()
            throughput.extend(vlc_evaluation.get_throughput())
            error.extend(vlc_evaluation.get_error())
    return max(throughput), max(error)

def plot_evaluation_rounds(result_directory, statistics_subdir, min_throughput, max_throughput,
                           min_error, max_error, stop_keyword="light_intensity"):
    for f in os.listdir(result_directory):
        path = result_directory + f
        if stop_keyword not in path:
            vlc_evaluation = DillSerializer(path).deserialize()
            throughput_error_plot(statistics_subdir, f, vlc_evaluation.get_throughput(), vlc_evaluation.get_error(),
                                  vlc_evaluation.get_data_period(), min_throughput, max_throughput, min_error, max_error)
            data = throughput_error_statistics(f, vlc_evaluation.get_throughput(), vlc_evaluation.get_error())
            misc.log(data, statistics_subdir, f)

def plot_manchester(result_directory, statistics_subdir,                    
                    min_throughput, max_throughput,
                    min_error, max_error,
                    stop_keyword="light_intensity"):
    for f in os.listdir(result_directory):
        if stop_keyword not in f and "manchester" in f:
            vlc_evaluation = DillSerializer(result_directory + f).deserialize()
            throughput_error_plot(statistics_subdir, f + "_series", vlc_evaluation.get_throughput(),
                                  vlc_evaluation.get_error(), vlc_evaluation.get_duration(),
                                  min_throughput, max_throughput, min_error, max_error)
            data = throughput_error_statistics(f, vlc_evaluation.get_throughput(),
                                               vlc_evaluation.get_error())
            misc.log(data, statistics_subdir, f)

def get_value(keyword, value):
    start = value.index(keyword) + len(keyword) + 1
    try:
        end = value.index("_", start)
    except ValueError:
        end = len(value)
    return int(value[start:end])

def barplot(subdir, filename, data_series, ymin, ymax,
            xlabels, labelyaxis, labelxaxis,
            width=0.6, marker_color="blue"):
    
    param_idx = None # find selected parameters
    if "50000" in filename:
        param_idx = xlabels.index(30)
    elif "130000" in filename:
        param_idx = xlabels.index(50)
    
    _, ax = plt.subplots()
    ind = numpy.arange(len(data_series))
    mean = numpy.mean(data_series, axis=1)
    std = numpy.std(data_series, axis=1)
    hatch = "\\\\\\" if "Error" in labelyaxis else "///"
    bars = ax.bar(ind, mean, width, yerr=std, facecolor="white", edgecolor="black",
                  align="center", capsize=4, hatch=hatch)
    # annotate zero mean values
    for i, bar in enumerate(bars):
        if "Throughput" in labelyaxis:
            if bar._height < 1.0:
                if i == param_idx:
                    ax.text(i, bar._height, "%.1f" % 0, horizontalalignment="center",
                            color=marker_color, fontweight="bold")
                else:
                    ax.text(i, bar._height, "%.1f" % 0, horizontalalignment="center")
        elif "Error" in labelyaxis:
            if bar._height < 0.001:
                if i == param_idx:
                    ax.text(i, bar._height, "%.1f" % 0, horizontalalignment="center",
                            color=marker_color, fontweight="bold")
                else:
                    ax.text(i, bar._height, "%.1f" % 0, horizontalalignment="center")
    
    ax.set_xlabel(labelxaxis)
    ax.set_ylabel(labelyaxis)
    ax.set_ylim(bottom=ymin, top=ymax)
    plt.grid(True, axis="y", linestyle=misc.plot_grid_linestyle)
    plt.xticks(ind, xlabels)
    plt.tight_layout()
    if param_idx: # highlight selected parameters
        bars[param_idx].set_facecolor(marker_color)
        #bars[param_idx].set_edgecolor(marker_color)
        #bars[param_idx].set_linewidth(3)
        ax.get_xticklabels()[param_idx].set_color(marker_color)
        ax.get_xticklabels()[param_idx].set_weight("bold")
    
    misc.savefig(subdir, filename)
    
def plot_summarized_evaluation_rounds(result_directory, statistics_subdir,
                                      min_throughput, max_throughput, max_error,
                                      stop_keyword="light_intensity", min_error=-0.015):    
    throughput = dict()
    error = dict()
    sampling_rates = set()
    time_base_units = set()
    for f in os.listdir(result_directory):
        path = result_directory + f
        if stop_keyword not in f and "morse" in f:
            vlc_evaluation = DillSerializer(path).deserialize()
            sampling = get_value("sampling", f)
            time_base_unit = get_value("time_base_unit", f)
            if sampling not in throughput:
                throughput[sampling] = dict()
                error[sampling] = dict()
            throughput[sampling][time_base_unit] = vlc_evaluation.get_throughput()
            error[sampling][time_base_unit] = vlc_evaluation.get_error()
            sampling_rates.add(sampling)
            time_base_units.add(time_base_unit)
    # Sort data
    filename = "morse-time-base-unit-%d"
    max_error *= 1.1
    for time_base_unit in sorted(time_base_units):
        series_error = []
        series_throughput = []
        for sampling_rate in sorted(sampling_rates)[:-1]: # remove last sampling rate
            series_throughput.append(numpy.nan_to_num(throughput[sampling_rate][time_base_unit]))
            series_error.append(numpy.nan_to_num(error[sampling_rate][time_base_unit]))
        subfile = (filename % time_base_unit) + "-throughput"
        xlabels = [xlabel/1000 for xlabel in sorted(sampling_rates)]
        barplot(statistics_subdir, subfile, series_throughput, min_throughput, max_throughput,
                xlabels, "Throughput (B/s)", u"Sampling interval (µs)")
        subfile = (filename % time_base_unit) + "-error"
        barplot(statistics_subdir, subfile, series_error, min_error, max_error,
                xlabels, "Error rate", u"Sampling interval (µs)")
        data = throughput_error_statistics(filename % time_base_unit, series_throughput, series_error)
        misc.log(data, statistics_subdir, filename % time_base_unit)

def throughput_ratio(result_directory, statistics_subdir):
    parameters_morse, throughput_morse = find_best_vlc_parameters(result_directory, "morse")
    parameters_manchester, throughput_manchester = find_best_vlc_parameters(result_directory, "manchester")
    data = "### Morse\n"
    data += parameters_morse + "\n"
    data += statistics.get_summary(throughput_morse) + "\n"
    data += "### Manchester\n"
    data += parameters_manchester + "\n"
    data += statistics.get_summary(throughput_manchester) + "\n"
    data += "ratio: " + str(round(numpy.mean(throughput_morse) / numpy.mean(throughput_manchester), 2))
    misc.log(data, statistics_subdir, "throughput_ratio")

def plot_comparison_morse_manchester(file_sizes, results_morse, results_manchester,
                                     xlabel, filename, evaluation,
                                     annotate_shift_morse, annotate_shift_manchester, xlim,
                                     bar_width=0.35):
    
    def annotate_y(rects, scaling_factors):
        if len(scaling_factors) == 1:
            scaling_factors = len(rects) * scaling_factors
        for rect, scaling_factor in zip(rects, scaling_factors):
            xloc = scaling_factor * rect.get_width()
            yloc = rect.get_y() + rect.get_height()/2.5
            ax.text(xloc, yloc, "%.2f" % rect.get_width(),
                    verticalalignment="center", horizontalalignment="right")
    
    fig, ax = plt.subplots()
    index = numpy.arange(len(file_sizes))
    manchester_rects = ax.barh(index + bar_width, numpy.mean(results_manchester, axis=1),
                               bar_width, xerr=numpy.std(results_manchester, axis=1),
                               label="Data encoding with Manchester code",
                               edgecolor="black", hatch="xx", color="white")
    annotate_y(manchester_rects, annotate_shift_manchester)
    morse_rects = ax.barh(index, numpy.mean(results_morse, axis=1), bar_width,
                          xerr=numpy.std(results_morse, axis=1), label="LocalVLC Encoding",
                          edgecolor="black", hatch="////", color="white")
    annotate_y(morse_rects, annotate_shift_morse)
    ax.set_yticks(index + bar_width / 2)
    ax.set_yticklabels([file_size/1024 for file_size in file_sizes])
    ax.set_ylabel("Message size (kB)")
    ax.set_xlabel(xlabel)
    ax.xaxis.grid(True)
    ax.set_xlim(right=xlim)
    ax.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=2, mode="expand", borderaxespad=0.)
    fig.set_figwidth(fig.get_figwidth()*2.5)
    data_path = os.path.join(files.dir_statistics, evaluation)
    plt.show()
    fig.savefig(os.path.join(data_path, filename + ".pdf"), format="pdf", bbox_inches='tight')

def light_intensity(result_directory, statistics_subdir):
    light_intensity_data = list()
    for f in os.listdir(result_directory):
        if "light_intensity" in f:
            path = result_directory + f
            light_intensity = [item["intensity"] for item in misc.read_json(open(path))]
            light_intensity_data.extend(light_intensity)
    data = statistics.get_summary(light_intensity_data)
    misc.log(data, statistics_subdir, "light_intensity")
    
def get_max_throughput_error(result_directory, max_factor=1.05):
    max_throughput, max_error = find_max_throughput_error(result_directory)
    max_throughput *= max_factor
    max_error *= max_factor
    return max_throughput, max_error

def vlc_parameters():
    data_directory = "vlc_parameters/"
    for led in ["pervasive_led", "directed_led"]:
        result_directory = files.dir_results + data_directory + led + "/"
        statistics_subdir = data_directory + led + "/"
        max_throughput, max_error = get_max_throughput_error(result_directory)
        if "pervasive" in led:
            min_throughput = -50
            min_error = -0.002
            light_intensity(result_directory, statistics_subdir)
            throughput_ratio(result_directory, statistics_subdir)
            plot_manchester(result_directory, statistics_subdir,
                            min_throughput, max_throughput, min_error, max_error)
            plot_summarized_evaluation_rounds(result_directory, statistics_subdir,
                                              min_throughput, max_throughput, max_error)
        else:
            min_throughput = -30
            min_error = -0.02
            parameters_morse, throughput_morse = find_best_vlc_parameters(result_directory, "morse")
            data = parameters_morse + "\n"
            data += statistics.get_summary(throughput_morse)
            misc.log(data, statistics_subdir, "throughput")
            plot_summarized_evaluation_rounds(result_directory, statistics_subdir,
                                              min_throughput, max_throughput, max_error)

def performance_morse_manchester():
    
    def get_data(sorted_file_sizes, datapaths, throughput=False, energy=False):
        if len(datapaths) > 0:
            data = list()
            basepath = datapaths[0]
            basepath = basepath[:basepath.rfind("-") + 1]
            for file_size in sorted_file_sizes:
                datapath = basepath + str(file_size)
                if throughput:
                    data.append(DillSerializer(datapath).deserialize().get_throughput_ratio())
                elif energy:
                    results = DillSerializer(datapath).deserialize()
                    energy_consumption_mJ = numpy.asarray(results.get_energy_consumption())
                    throughput_total = numpy.asarray(results.get_throughput_total())
                    data.append(energy_consumption_mJ / throughput_total)
            return data
        return None
    
    evaluation = "vlc-performance"
    results_morse = glob.glob(os.path.join(files.dir_results, evaluation, "morse-*"))
    results_manchester = glob.glob(os.path.join(files.dir_results, evaluation, "manchester-*"))
    file_sizes = sorted([int(os.path.basename(path).split("-")[-1]) for path in results_manchester])
    
    energy_morse = get_data(file_sizes, results_morse, energy=True)
    energy_manchester = get_data(file_sizes, results_manchester, energy=True)
    plot_comparison_morse_manchester(file_sizes, energy_morse, energy_manchester,
                                     "Energy (mJ/B)", "energy-receiver-morse-manchester", evaluation,
                                     [1.6, 1.7, 1.7, 1.8], [1.11, 1.09, 1.09, 1.09], 17.2)
    
    throughput_morse = get_data(file_sizes, results_morse, throughput=True)
    throughput_manchester = get_data(file_sizes, results_manchester, throughput=True)
    plot_comparison_morse_manchester(file_sizes, throughput_morse, throughput_manchester,
                                     "Throughput (B/s)", "throughput-morse-manchester", evaluation,
                                     [1.31, 1.16, 1.16, 1.17], [2.1], 1350)
    
def main():
    vlc_parameters()
    performance_morse_manchester()
    
if __name__ == "__main__":
    main()
