import os
import numpy
import localvlc.misc as misc
import localvlc.files as files
import utils.statistics as statistics
import matplotlib.pyplot as plt
from utils.serializer import DillSerializer
from matplotlib.ticker import FormatStrFormatter

def print_statistics(statistics_subdir, filename, data):
    throughput = list()
    error = list()
    for performance in data.values():
        throughput.extend(performance.get_throughput())
        error.extend(performance.get_error())
    data = "### Throughput" + "\n" + \
    statistics.get_summary(throughput) + "\n" + \
    "------------------------\n" + \
    "### Error"  + "\n" + \
    statistics.get_summary(error)
    misc.log(data, statistics_subdir, filename)

def throughput_error_plot(statistics_subdir, filename, data, max_distance, min_throughput,
                          max_throughput, min_error, max_error, show_max_distance=False):
    fig, ax1 = plt.subplots()
    ax2 = ax1.twinx()
    i = 0
    throughput = list()
    error = list()
    xvalues = list()
    xticks = list()
    for distance, performance in sorted(data.items()):
        #throughput.append(numpy.mean(misc.reject_outliers(numpy.array(performance.get_throughput()))))
        #error.append(numpy.mean(misc.reject_outliers(numpy.array(performance.get_error()))))
        throughput.append(numpy.median(performance.get_throughput()))
        error.append(numpy.median(performance.get_error()))
        xvalues.append(distance)
        if distance % 1 == 0.0 or i == 0 or (i+1) == len(data):
            xticks.append(distance)
        i += 1
    p1, = ax1.plot(xvalues, throughput, marker="D", label="Throughput", color="b")    
    p2, = ax2.plot(xvalues, error, marker="s", label="Error rate", color="r")
    if len(xticks) <= 5:
        ax1.set_xticks(xticks)
    else:
        ax1.set_xticks(xticks[1:])
    
    if show_max_distance:
        p3 = ax1.axvline(x=max_distance, color="k", linestyle="--", label="Max. distance")
        offset = 0.7 if len(data) > 6 else 0.2
        ax1.annotate(max_distance, xy=(max_distance-offset, max_throughput*0.2), color=p3.get_color())
    ax1.set_xlabel("Max. distance (m)")
    ax1.set_ylabel("Throughput (B/s)", color=p1.get_color())
    ax2.set_ylabel("Error rate", color=p2.get_color())
    ax2.yaxis.set_major_formatter(FormatStrFormatter('%.2f'))
    ax1.tick_params(axis='y', colors=p1.get_color())
    ax2.tick_params(axis='y', colors=p2.get_color())
    ax1.set_ylim(bottom=min_throughput, top=max_throughput)
    ax2.set_ylim(bottom=min_error, top=max_error)
    if show_max_distance:
        lines = [p1] + [p2] + [p3]
    else:
        lines = [p1] + [p2]
    labels = [l.get_label() for l in lines]
    plt.legend(lines, labels, bbox_to_anchor=(0., 1.02, 1., .105),
               loc="lower left", ncol=3, mode="expand", borderaxespad=0.)
    fig.set_figwidth(fig.get_figwidth()*1.35, forward=True)
    plt.subplots_adjust(left=0.15, right=0.99, bottom=0.15)
    plt.grid(True, axis="y", linestyle=misc.plot_grid_linestyle)
    plt.tight_layout(rect=[0, 0, 1, .95])
    misc.savefig(statistics_subdir, filename)
    
def get_distance(value, search_term="led"):
    start = value.index(search_term) + len(search_term) + 1
    return float(value[start:len(value)-2].replace("_", "."))

def find_max_throughput_error(vlc_evaluations, max_factor=1.05):
    error = list()
    throughput = list()
    for vlc_evaluation in vlc_evaluations.values():
        throughput.extend(vlc_evaluation.get_throughput())
        error.extend(vlc_evaluation.get_error())
    return max(throughput)*max_factor, max(error)*max_factor

def main():
    data_directory = "vlc_distance/"
    result_directory = files.dir_results + data_directory
    statistics_subdir = data_directory
    distance_directed_led = dict()
    distance_pervasive_led = dict()
    
    for f in os.listdir(result_directory):
        if "light_intensity" in f:
            path = result_directory + f
            light_intensity = [item["intensity"] for item in misc.read_json(open(path))]
            data = statistics.get_summary(light_intensity)            
            misc.log(data, statistics_subdir, f)
        elif "morse" in f:
            distance = get_distance(f)
            path = result_directory + f
            vlc_evaluation = DillSerializer(path).deserialize()
            if "directed_led" in f:
                distance_directed_led[distance] = vlc_evaluation
            elif "pervasive_led" in f:
                distance_pervasive_led[distance] = vlc_evaluation
    
    min_throughput = -50
    min_error = -0.008
    
    max_throughput_pervasive, max_error_pervasive = find_max_throughput_error(distance_pervasive_led)
    max_throughput_directed, max_error_directed = find_max_throughput_error(distance_directed_led)
    max_throughput = max(max_throughput_pervasive, max_throughput_directed)
    max_error = max(max_error_pervasive, max_error_directed)
    
    filename = "directed_led"
    throughput_error_plot(statistics_subdir, filename, distance_directed_led, 4.30,
                          min_throughput, max_throughput, min_error, max_error)
    print_statistics(statistics_subdir, filename, distance_directed_led)
    
    filename = "pervasive_led"
    throughput_error_plot(statistics_subdir, filename, distance_pervasive_led, 1.60,
                          min_throughput, max_throughput, min_error, max_error)
    print_statistics(statistics_subdir, filename, distance_pervasive_led)
    
if __name__ == "__main__":
    main()
