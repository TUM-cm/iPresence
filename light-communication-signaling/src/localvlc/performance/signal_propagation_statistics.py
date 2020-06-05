from __future__ import division
import os
import numpy
import subprocess
import scipy.interpolate
import localvlc.files as files
import localvlc.misc as misc
import matplotlib.pyplot as plt
from utils.serializer import DillSerializer

subdir = "signal_propagation/"
# Measurement points
measurement_points = dict()
for j, i in zip(range(1, 70, 3), range(1, 70, 1)):
    measurement_points[j] = (1, i)
    measurement_points[j+1] = (2, i)
    measurement_points[j+2] = (3, i)
measurement_points[70] = (1, 24)
measurement_points[71] = (2, 24)
measurement_points[72] = (1, 25)
measurement_points[73] = (2, 25)
max_x = -1
max_y = -1
for (x, y) in measurement_points.values():
    if x > max_x:
        max_x = x
    if y > max_y:
        max_y = y

def heatmap(x, y, z, name, bottom_limit=None, top_limit=None, invert_xaxis=False, delta=0.01):
    xi = numpy.arange(x[0], x[-1]+delta*0.1, delta)
    yi = numpy.arange(y[0], y[-1]+delta*0.1, delta)
    xi, yi = numpy.meshgrid(xi, yi)
    interpolated_z = scipy.interpolate.interpn((x, y), z, (xi, yi), method='splinef2d')    
    if top_limit != None:
        interpolated_z[interpolated_z > top_limit] = top_limit
    if bottom_limit != None:
        interpolated_z[interpolated_z < bottom_limit] = bottom_limit
    if invert_xaxis:
        interpolated_z[interpolated_z < -20] = interpolated_z[interpolated_z < -20] + 20
    imgplot = plt.imshow(interpolated_z)
    plt.gca().invert_yaxis()
    if invert_xaxis:
        plt.gca().invert_xaxis()
        imgplot.set_cmap('Spectral_r')
    else:
        imgplot.set_cmap('Spectral')
    plt.axis('off')
    plt.colorbar()
    misc.savefig(subdir, name, "svg")
    if not misc.plot_show:
        inkscape_path = "C://Program Files//Inkscape//inkscape.exe"
        svg_file = files.dir_statistics + subdir + name + ".svg"
        emf_file = files.dir_statistics + subdir + name + ".emf"
        subprocess.call([inkscape_path, svg_file, "--export-emf", emf_file])
        os.remove(svg_file)
    plt.clf()

def get_summarized_data(indices, data_in, light=False):
    data_out = []
    for idx in indices:
        if light:
            raw_data = data_in[idx]
            raw_data = raw_data.get_error()
        else:
            raw_data = data_in[str(idx)]
            if len(raw_data) == 1 and raw_data[0] == 0.0:
                raw_data = [-100]
        if len(raw_data) > 1:
            data_out.extend(misc.reject_outliers(numpy.array(raw_data)))
        else:
            data_out.extend(raw_data)
    return numpy.mean(data_out)

def bluetooth(x, y):
    f = misc.open_file("bluetooth.dat")
    signal_propagation_bluetooth = misc.read_json(f)
    for idx in range(50, 70, 1):
        data = signal_propagation_bluetooth[str(idx)]
        print idx
        print numpy.mean(misc.reject_outliers(numpy.array(data)))
        print "----------------"
    min_rssi = -300
    for _, data in signal_propagation_bluetooth.items():
        rssi = numpy.mean(misc.reject_outliers(numpy.array(data)))
        if rssi > min_rssi and rssi != 0.0:
            min_rssi = rssi
    print "min rssi: ", min_rssi    
    z_rssi = numpy.zeros((x.size, y.size), dtype=numpy.float32) # zero - smallest signal strength
    for i in range(1, len(measurement_points)):
        z_rssi[measurement_points[i]] = get_summarized_data([i], signal_propagation_bluetooth)
    heatmap(x, y, z_rssi, "bluetooth", top_limit=0, invert_xaxis=True)

def light(x, y):
    path = files.dir_results + "signal_propagation/light"
    signal_propagation_light = DillSerializer(path).deserialize()
    z_error_rate = numpy.ones((x.size, y.size), dtype=numpy.float32) # one - highest error
    measurement_1 = get_summarized_data([1,2,3,4], signal_propagation_light, True)
    measurement_2 = get_summarized_data([7,8], signal_propagation_light, True)
    measurement_3 = get_summarized_data([5,6], signal_propagation_light, True)
    z_error_rate[measurement_points[60]] = measurement_1
    z_error_rate[measurement_points[63]] = measurement_2
    z_error_rate[measurement_points[57]] = measurement_3
    heatmap(x, y, z_error_rate, "light", bottom_limit=0, top_limit=1)
    
def main():
    x = numpy.arange(max_x+1)
    y = numpy.arange(max_y+1)
    bluetooth(x, y)
    
    x = numpy.arange(max_x+2)
    y = numpy.arange(max_y+1)
    light(x, y)

if __name__ == "__main__":
    main()
