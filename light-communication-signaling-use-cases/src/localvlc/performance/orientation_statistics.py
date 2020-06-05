# -*- coding: utf-8 -*- 
import os
import numpy
import matplotlib
import localvlc.misc as misc
import localvlc.files as files
import matplotlib.pyplot as plt
from utils.serializer import DillSerializer
import localvlc.performance.parameter_statistics as parameters

# directed LED: up 85, down -85
# pervasive LED: up 50, down -65
def orientation_performance(result_directory, statistics_subdir):
    min_throughput = -50
    min_error = -0.008
    max_throughput, max_error = parameters.get_max_throughput_error(result_directory)
    for f in os.listdir(result_directory):
        path = result_directory + f
        vlc_evaluation = DillSerializer(path).deserialize()
        parameters.throughput_error_plot(statistics_subdir, f, vlc_evaluation.get_throughput(),
                                         vlc_evaluation.get_error(), vlc_evaluation.duration_data, #vlc_evaluation.get_data_period(),
                                         min_throughput, max_throughput, min_error, max_error)
        data = parameters.throughput_error_statistics(f, vlc_evaluation.get_throughput(), vlc_evaluation.get_error())
        misc.log(data, statistics_subdir, f)

def orientation(statistics_subdir):
    font = {'size' : 15}
    matplotlib.rc('font', **font)
    ax = plt.subplot(111, polar=True)
    ax.set_thetamin(0)
    ax.set_thetamax(180)
    ax.grid(False)
    ax.set_yticklabels([0])
    ax.set_xticks(numpy.pi/180. * numpy.linspace(0, 180, 5))
    
    # 90 grad = 1.57 width
    #bars = ax.bar(np.radians(0), 2, width=1.57)
    #bars = ax.bar(np.radians(0), 2, width=2.97)
    ax.bar(numpy.radians(90), 2, width=2.97, fill=False, hatch="...", label="Directional LED")
    ax.bar(numpy.radians(90 + 17.5), 1.5, width=2.01, color="white", edgecolor="black", hatch="+++", label="Omnidirectional LED")
    
    ax.annotate(u'50°', xy=(numpy.radians(70), 1.1), backgroundcolor="white")
    ax.annotate(u'165°', xy=(numpy.radians(155), 1.3), backgroundcolor="white")
    ax.annotate(u'5°', xy=(numpy.radians(11), 1.6), backgroundcolor="white")
    ax.annotate(u'175°', xy=(numpy.radians(170), 1.9), backgroundcolor="white")
    #ax.legend(bbox_to_anchor=(0., 0.85, 1., .102), loc=3, ncol=1, mode="expand", borderaxespad=0.)
    ax.legend(loc="center left", bbox_to_anchor=(1, 0.5))
    #plt.tight_layout()
    #plt.show()
    misc.savefig(statistics_subdir, "angle", ending="pdf")

def main():
    data_directory = "vlc_orientation/"
    statistics_subdir = data_directory    
    result_directory = files.dir_results + data_directory
    
    orientation(statistics_subdir)
    orientation_performance(result_directory, statistics_subdir)
    
if __name__ == "__main__":
    main()
