import os
import localvlc.misc as misc
import localvlc.files as files
import matplotlib.pyplot as plt
import utils.statistics as statistics
from utils.serializer import DillSerializer

def latency_plot(statistics_subdir, latency, min_latency, max_latency, xlabel="Evaluation round",
                 ylabel="Latency (s)", filename="latency", xticks=True, legend_outside=True):
    _, ax = plt.subplots()
    xvalues = range(1, len(list(latency.values())[0])+1)
    for key in latency:
        if "directed" in key:
            ax.plot(xvalues, latency[key], marker="D", label="Directional LED", color="b")      
        elif "pervasive" in key:
            ax.plot(xvalues, latency[key], marker="s", label="Pervasive LED",  color="g")
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.tick_params(axis='y')
    if xticks:
        plt.xticks(xvalues)
    ax.set_ylim(bottom=min_latency, top=max_latency)
    if legend_outside:
        ax.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc="lower left",
                   ncol=len(latency), mode="expand", borderaxespad=0.)
        plt.tight_layout(rect=[0, 0, 1, .95])
    else:
        ax.legend()
        plt.tight_layout()
    ax.grid(True, axis="y", linestyle=misc.plot_grid_linestyle)
    misc.savefig(statistics_subdir, filename)
    
def latency_statistics(filename, latency):
    result = filename + "\n"
    result += "\n### Latency ###\n"
    result += statistics.get_summary(latency)
    return result

def plot_evaluation_rounds(result_directory, statistics_subdir,
                           min_latency, max_latency, stop_keyword="light_intensity"):
    latency = dict()
    for f in os.listdir(result_directory):
        if stop_keyword not in f:
            path = result_directory + f                    
            vlc_evaluation = DillSerializer(path).deserialize()
            latency[f] = vlc_evaluation.get_latency()
            data = latency_statistics(f, vlc_evaluation.get_latency())
            misc.log(data, statistics_subdir, f)
    latency_plot(statistics_subdir, latency, min_latency, max_latency)
    
def find_max_latency(result_directory, stop_keyword="light_intensity"):
    latency = list()
    for f in os.listdir(result_directory):
        if stop_keyword not in f:
            path = result_directory + f
            vlc_evaluation = DillSerializer(path).deserialize()
            latency.extend(vlc_evaluation.get_latency())
    return max(latency)

def main():
    data_directory = "vlc_latency/"
    result_directory = files.dir_results + data_directory
    statistics_subdir = data_directory
    min_latency = -0.02
    max_latency = find_max_latency(result_directory)
    max_latency *= 1.1
    plot_evaluation_rounds(result_directory, statistics_subdir, min_latency, max_latency)
    
if __name__ == "__main__":
    main()
