import os
import glob
import dill
import numpy
import random
import matplotlib
import collections
from scipy import stats
from itertools import tee            
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from matplotlib.ticker import NullFormatter
from matplotlib.ticker import ScalarFormatter
# Monsoon API for energy measurements
try:
    import Monsoon.HVPM as HVPM
    import Monsoon.sampleEngine as sampleEngine
except:
    pass

'''
Install libusb driver for Windows to communicate with Monsoon power monitor
https://github.com/libusb/libusb/wiki/Windows

1. Install https://zadig.akeo.ie for USB driver installation
2. List all devices
3. Select "Mobile Device Power Monitor"
4. Install libusb-win32 driver

Afterwards you are able to communicate with Monsoon via PyMonsoon: https://github.com/msoon/PyMonsoon

Measurement tutorials:
* https://mostly-tech.com/tag/monsoon-power-monitor/
* https://tqrg.github.io/physalia/monsoon_tutorial.html
* https://www.youtube.com/watch?v=zTPAvKjucnc
'''

# Set global matplotlib parameters
font = {'size' : 22}
matplotlib.rc('font', **font)
matplotlib.rcParams["pdf.fonttype"] = 42 # TrueType
matplotlib.rcParams["ps.fonttype"] = 42 # TrueType

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

# A * V = W
# A = W / V
# Wh / V = Ah
# W = J / s > J = W * s

class Measurements:
    
    def __init__(self):
        self.currents = None
        self.voltages = None
        self.timestamps = None
        self.sensor_readings = None

class DillSerializer:
    
    def __init__(self, path):
        self.path = path
    
    def serialize(self, obj):
        f = open(self.path, "wb+")
        dill.dump(obj, f)
        f.close()
        
    def deserialize(self):
        f = open(self.path, "rb")
        data = dill.load(f)
        f.close()
        return data

def setup_voltage(device_voltage):
    HVMON = HVPM.Monsoon()
    HVMON.setup_usb()
    print("HVPM Serial Number: " + repr(HVMON.getSerialNumber()))
    HVMON.fillStatusPacket()
    HVMON.setVout(device_voltage)
    HVMON.closeDevice()
    
def calculate_energy(measurement):
    energy_Wh = list()
    for I_mA, U_V, t_s in zip(measurement.currents, measurement.voltages, numpy.diff(measurement.timestamps)):
        # E = P * t = U * I * t    
        energy_mWh = U_V * I_mA * (t_s / 3600.0) # t[s] to t[h], mA * V * h
        energy_Wh.append(energy_mWh / 1000)
    energy_Wh = sum(energy_Wh)
    energy_J = energy_Wh * 3600 # 1 Wh = 3600 Joule
    print("energy (J):", round(energy_J, 2))
    return energy_J

class EnergyMeasurements:
    
    def __init__(self, testbed, result_path):
        self.measurements = Measurements()
        self.filepath = os.path.join(result_path, testbed)
        self.serializer = DillSerializer(self.filepath)
        self.HVMON, self.HVengine = self.__create_engine()
    
    def __create_engine(self):
        HVMON = HVPM.Monsoon()
        HVMON.setup_usb()
        print("HVPM Serial Number: " + repr(HVMON.getSerialNumber()))
        HVMON.fillStatusPacket()
        #HVMON.setVout(device_voltage)
        HVengine = sampleEngine.SampleEngine(HVMON)
        HVengine.ConsoleOutput(False)
        HVengine.disableCSVOutput()
        #HVengine.enableChannel(sampleEngine.channels.MainCurrent)
        #HVengine.enableChannel(sampleEngine.channels.MainVoltage)
        #HVengine.enableChannel(sampleEngine.channels.timeStamp)
        return HVMON, HVengine
    
    def measure(self, duration, nth=50):
        numSamples = sampleEngine.triggers.SAMPLECOUNT_INFINITE
        self.HVengine.setStartTrigger(sampleEngine.triggers.GREATER_THAN, 0)
        self.HVengine.setStopTrigger(sampleEngine.triggers.GREATER_THAN, duration)
        self.HVengine.setTriggerChannel(sampleEngine.channels.timeStamp)
        print("Start sampling ...")
        self.HVengine.startSampling(numSamples)
        print("Done sampling ...")
        samples = self.HVengine.getSamples()
        self.measurements.currents = samples[sampleEngine.channels.MainCurrent][0::nth]
        self.measurements.voltages = samples[sampleEngine.channels.MainVoltage][0::nth]
        self.measurements.timestamps = samples[sampleEngine.channels.timeStamp][0::nth]
        self.HVMON.closeDevice()
        print("Results ...")
        calculate_energy(self.measurements)
    
    def save_results(self):
        print("Save results ...")
        self.serializer.serialize(self.measurements)

def perform_measurements(result_path):
    testbed = "location-network"
    activate_monsoon = True
    
    device_voltage = 3.85
    evaluation_period = 300
    if activate_monsoon:
        setup_voltage(device_voltage)
    else:
        energy_measurements = EnergyMeasurements(testbed, result_path)
        energy_measurements.measure(evaluation_period)
        if "idle" not in testbed:
            sensor_readings = int(input("Please enter sensor readings: "))
            energy_measurements.measurements.sensor_readings = sensor_readings
        energy_measurements.save_results()

def generate_dummy_data_temp_humidity(result_path):
    light = DillSerializer(os.path.join(result_path, "light")).deserialize()
    for sensor in ["temperature", "humidity"]:
        scale = random.uniform(1.005, 1.03)
        light.currents = numpy.asarray(light.currents) * scale
        light.sensor_readings = int(light.sensor_readings * random.uniform(1.05, 1.1))
        DillSerializer(os.path.join(result_path, sensor)).serialize(light)
    
def analyze_measurements(measurements_path):
    
    def pairwise(iterable):
        a, b = tee(iterable)
        next(b, None)
        return zip(a, b)
    
    def calculate_energy_per_reading_old(result_path, filename_idle="idle"):
        idle_path = os.path.join(result_path, filename_idle)
        idle_measurements = DillSerializer(idle_path).deserialize()
        print("idle energy")
        idle_energy_J = calculate_energy(idle_measurements)
        path_energy_readings = set(glob.glob(os.path.join(result_path, "*"))) - set(glob.glob(idle_path))
        for path_energy_reading in list(path_energy_readings):
            print("#" + os.path.basename(path_energy_reading))
            sensor_measurements = DillSerializer(path_energy_reading).deserialize()
            print("sensor energy")
            sensor_energy_J = calculate_energy(sensor_measurements)
            plain_sensor_energy_J = abs(sensor_energy_J - idle_energy_J)
            print("plain energy (mJ):", round(plain_sensor_energy_J*1000, 2))
            print("sensor readings:", sensor_measurements.sensor_readings)
            print("plain energy (mJ) per reading", round((plain_sensor_energy_J*1000) / sensor_measurements.sensor_readings, 2))
    
    def calculate_energy_per_reading(result_path, filename_idle="idle", data_ranges=5):
        
        def get_sub_measurements(measurements, start, end, n_ranges=None):
            sub_measurements = Measurements()
            sub_measurements.currents = measurements.currents[start:end]
            sub_measurements.voltages = measurements.voltages[start:end]
            sub_measurements.timestamps = measurements.timestamps[start:end]
            if n_ranges:
                sub_measurements.sensor_readings = measurements.sensor_readings/n_ranges
            return sub_measurements
     
        def detect_by_cusum(data):
            min_val = numpy.min(data)
            max_val = numpy.max(data)
            likelihood = min_val + ((max_val - min_val)/2)
            cusum = numpy.empty(data.shape[0])
            cusum_val = 0
            for i in range(data.shape[0]):
                cusum_val = max(0, cusum_val + data[i] - likelihood)
                cusum[i] = cusum_val
            threshold = numpy.median(cusum)
            return numpy.where(cusum <= threshold)
        
        def detect_by_fft(signal, threshold_freq=.1, frequency_amplitude=.01):
            fft_of_signal = numpy.fft.fft(signal)
            f = numpy.fft.fftfreq(len(fft_of_signal), 0.001)
            outlier = numpy.max(signal) if abs(numpy.max(signal)) > abs(numpy.min(signal)) else numpy.min(signal)
            if numpy.any(numpy.abs(fft_of_signal[f>threshold_freq]) > frequency_amplitude):
                return numpy.where(signal != outlier)
            
        def detect_by_iqr(signal, bottom=25, top=75, threshold=1.5):
            quartile_1, quartile_3 = numpy.percentile(signal, [bottom, top])
            iqr = quartile_3 - quartile_1
            lower_bound = quartile_1 - (iqr * threshold)
            upper_bound = quartile_3 + (iqr * threshold)
            return numpy.where((signal < upper_bound) & (signal > lower_bound))
        
        def detect_by_median(signal):
            difference = numpy.abs(signal - numpy.median(signal))
            median_difference = numpy.median(difference)
            median_ratio = 0 if median_difference == 0 else difference / float(median_difference)
            threshold = numpy.median(median_ratio)
            return numpy.where(median_ratio <= threshold)
        
        # http://colingorrie.github.io/outlier-detection.html
        def detect_by_modified_z_score(signal):
            median_y = numpy.median(signal)
            median_absolute_deviation_y = numpy.median([numpy.abs(y - median_y) for y in signal])
            modified_z_scores = [0.6745 * (y - median_y) / median_absolute_deviation_y for y in signal]
            modified_z_scores = numpy.abs(modified_z_scores)
            threshold = numpy.median(modified_z_scores)
            return numpy.where(modified_z_scores <= threshold)
        
        def detect_by_zscore(ys):
            mean_y = numpy.mean(ys)
            stdev_y = numpy.std(ys)
            z_scores = numpy.abs([(y - mean_y) / stdev_y for y in ys])
            threshold = numpy.median(z_scores)
            return numpy.where(z_scores <= threshold)
        
        # same result as own zscore
        def detect_by_zscore_scipy(signal):
            zscores = numpy.abs(stats.zscore(signal))
            threshold = numpy.median(zscores)
            return numpy.where(zscores <= threshold)
    
        sensors = list()
        energy_mean_mJ = list()
        energy_std_mJ = list()
        energy_median_mJ = list()
        idle_path = os.path.join(result_path, filename_idle)
        idle_measurements = DillSerializer(idle_path).deserialize()
        path_energy_readings = set(glob.glob(os.path.join(result_path, "*"))) - set(glob.glob(idle_path))
        for path_energy_reading in list(path_energy_readings):
            sensor_name = os.path.basename(path_energy_reading)
            sensor_measurements = DillSerializer(path_energy_reading).deserialize()
            energy_per_reading_mJ = list()
            total_datalen = len(sensor_measurements.timestamps)
            chunk_datalen = int(total_datalen/data_ranges)
            print("#" + sensor_name)
            for start in range(0, total_datalen, chunk_datalen):
                end = start + chunk_datalen
                if end > total_datalen:
                    continue
                idle_sub_measurements = get_sub_measurements(idle_measurements, start, end)
                print("idle energy")
                idle_energy_J = calculate_energy(idle_sub_measurements)
                sensor_sub_measurements = get_sub_measurements(sensor_measurements, start, end, data_ranges)
                print("sensor energy")
                sensor_energy_J = calculate_energy(sensor_sub_measurements)
                plain_sensor_energy_J = abs(sensor_energy_J - idle_energy_J)
                print("plain energy (mJ):", round(plain_sensor_energy_J * 1000, 2))
                print("sensor readings:", sensor_sub_measurements.sensor_readings)
                print("plain energy (mJ) per reading:", round((plain_sensor_energy_J * 1000) / sensor_sub_measurements.sensor_readings, 2))
                energy_per_reading_mJ.append((plain_sensor_energy_J * 1000) / sensor_sub_measurements.sensor_readings)
            
            energy_per_reading_mJ = numpy.asarray(energy_per_reading_mJ)
            inliers = detect_by_zscore(energy_per_reading_mJ)
            #inliers = detect_by_modified_z_score(energy_per_reading_mJ)
            #inliers = detect_by_zscore_scipy(energy_per_reading_mJ)
            #inliers = detect_by_median(energy_per_reading_mJ)
            #inliers = detect_by_cusum(energy_per_reading_mJ)
            #inliers = detect_by_fft(energy_per_reading_mJ)
            #inliers = detect_by_iqr(energy_per_reading_mJ)
            energy_per_reading_mJ = energy_per_reading_mJ[inliers]
            #print("energy (mj) per reading", numpy.mean(energy_per_reading_mJ), numpy.std(energy_per_reading_mJ))
            
            sensors.append(sensor_name)
            energy_mean_mJ.append(numpy.mean(energy_per_reading_mJ))
            energy_std_mJ.append(numpy.std(energy_per_reading_mJ))
            energy_median_mJ.append(numpy.median(energy_per_reading_mJ))
        
        return sensors, energy_mean_mJ, energy_std_mJ, energy_median_mJ
    
    def identify_energy_clusters(sensor_names, energy_median_mJ, num_clusters=3):
        kmeans = KMeans(n_clusters=num_clusters)
        kmeans.fit(numpy.asarray(energy_median_mJ).reshape(-1, 1))
        sensor_clusters = collections.defaultdict(list)
        for i, cluster in enumerate(kmeans.labels_):
            sensor_clusters[cluster].append(sensor_names[i])
        
        sensor_cluster_energy_mJ = kmeans.cluster_centers_.ravel()
        for cluster, sensors in sensor_clusters.items():
            print("cluster", cluster, sensors, "energy (mJ)", round(sensor_cluster_energy_mJ[cluster], 1))
        sensor_cluster_centers = dict(zip(range(len(sensor_clusters)), sensor_cluster_energy_mJ))
        sensor_cluster_centers = sorted(sensor_cluster_centers.items(), key=lambda kv: kv[1])
        for (cluster1, energy1), (cluster2, energy2) in pairwise(sensor_cluster_centers):
            print("cluster:", cluster1, "cluster:", cluster2, "ratio (times):", round(energy2 / energy1, 1))
    
    def plot_sensor_energy(sensors, energy_mean, energy_std, labels, result_path, plot_format):
        
        def autolabel(ax, rects):
            for y, rect in enumerate(rects):
                width = rect.get_width()
                x = width * 1.8
                if width > 5:
                    x -= x*0.95
                ax.text(x, y, "%.1f" % width, va="center", bbox=dict(boxstyle='square,pad=0', facecolor="white", edgecolor="none"))
        
        sensors, energy_mean, energy_std = zip(*sorted(zip(sensors, energy_mean, energy_std), key=lambda x: x[1]))
        fig, ax = plt.subplots()
        sensors = [labels[sensor] if sensor in labels else sensor.capitalize() for sensor in sensors]
        rects = ax.barh(sensors, energy_mean, xerr=energy_std, height=0.7, hatch="////",
                        error_kw=dict(capsize=5, capthick=3, lw=3), edgecolor="black", fill=False, log=True)
        autolabel(ax, rects)
        ax.xaxis.grid(True, linestyle="dotted")
        ax.xaxis.set_major_formatter(ScalarFormatter())
        ax.set_xlabel("Energy (mJ) per sensor action")
        
        energy_clusters = dict()
        energy_clusters["small"] = ["barometer", "accelerometer", "magnetometer", "light", "BLE scan", "GSM scan"]
        energy_clusters["mid"] = ["Bluetooth discovery", "network location", "Wi-Fi scan"]
        energy_clusters["high"] = ["GPS location"]
        
        label_color = "red"
        vertical_offset = 0
        horizontal_offset = -0.74
        
        for i, (energy_level, sensors) in enumerate(energy_clusters.items()):
            positions = range(vertical_offset, vertical_offset+len(sensors))
            yposition = numpy.mean(positions)
            xposition = int(round(yposition))
            xposition = (energy_mean[xposition] + energy_std[xposition]) * 1.3
            if "small" in energy_level:
                xposition *= 5
            ax.text(xposition, yposition, energy_level, color=label_color, va="center",
                    bbox=dict(boxstyle='square,pad=0', facecolor="white", edgecolor="none"))
            
            vertical_offset += len(sensors)
            if (i+1) != len(energy_clusters):
                ax.axhline(vertical_offset-0.5, xmin=horizontal_offset, color=label_color, linestyle="--", linewidth=2, clip_on=False)
        
        fig.set_figheight(fig.get_figheight()*1.3)
        fig.set_figwidth(fig.get_figwidth()*1.16)
        ax.set_xlim(right=22e3)
        filename = os.path.join(result_path, "energy-sensor" + "." + plot_format)
        fig.savefig(filename, format=plot_format, bbox_inches="tight")
        #plt.show()
        plt.close(fig)
    
    def battery_lifetime(idle_path, sensor_energies_mJ, labels, result_path, plot_format, filename_idle="idle"):
        
        def plot_ratio_idle_sensor_energy(sensors, idle_energy, sensor_energy, idle_energy_ratio, sensor_energy_ratio):
            
            def autolabel(ax, values, rects):
                for value, rect in zip(values, rects):
                    yoffset = 0.02
                    scaling = 1.05
                    if value > 0.03/100 and value < 5/100:
                        scaling = 0.02
                    elif value > 5/100:
                        scaling = 0.02
                    else:
                        yoffset = -0.02
                    x = scaling * rect.get_width()
                    y = rect.get_y() + yoffset
                    ax.text(x, y, "{:.4%}".format(value), va="bottom",
                            bbox=dict(boxstyle='square,pad=0', facecolor="white", edgecolor="none"))
            
            sensor_energy, idle_energy, sensor_energy_ratio, idle_energy_ratio, sensors \
                = zip(*sorted(zip(sensor_energy, idle_energy, sensor_energy_ratio, idle_energy_ratio, sensors)))
            fig, ax = plt.subplots()
            barwidth = 0.45
            barspace = 0 + numpy.arange(len(sensors)) * 0.2
            r1 = numpy.arange(len(sensors)) + barspace
            r2 = r1 + barwidth
            rects = ax.barh(r2, idle_energy, barwidth, edgecolor="black", fill=False, hatch="////", label="System idle", log=True)
            autolabel(ax, idle_energy_ratio, rects)
            rects = ax.barh(r1, sensor_energy, barwidth, edgecolor="black", fill=False, hatch="xxxx", label="Sensor action", log=True)
            autolabel(ax, sensor_energy_ratio, rects)
            temp = [labels[sensor] if sensor in labels else sensor.capitalize() for sensor in sensors]
            for l, label in enumerate(temp):
                new_label = ""
                parts = label.split()
                pos = (len(parts)/2)-1
                for i, part in enumerate(parts):
                    delimeter = "\n" if i==pos else " "
                    new_label += (part + delimeter)
                temp[l] = new_label.strip()
            ax.set_yticks(r1 + barwidth/2)
            ax.set_yticklabels(temp)
            ax.set_xlabel("System's battery capacity (J)")
            ax.xaxis.grid(True, linestyle="dotted")
            ax.xaxis.set_major_formatter(ScalarFormatter())
            ax.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=2, mode="expand", borderaxespad=0.)
            fig.set_figheight(fig.get_figheight()*2.5)
            fig.set_figwidth(fig.get_figwidth()*1.25)
            filename = os.path.join(result_path, "energy-ratio-idle-sensor" + "." + plot_format)
            fig.savefig(filename, format=plot_format, bbox_inches="tight")
            #plt.show()
            plt.close(fig)
        
        def plot_runtime(sensors, runtimes, labels, result_path, plot_format):
            
            def autolabel(ax, rects):
                for y, rect in enumerate(rects):
                    width = rect.get_width()
                    x = width + width*0.0001
                    if x > 17.3:
                        x -= x*0.006
                    ax.text(x, y, "%.2f" % width, va="center", bbox=dict(boxstyle='square,pad=0', facecolor="white", edgecolor="none"))
            
            runtimes, sensors = zip(*sorted(zip(runtimes, sensors)))
            duration_min = (runtimes[-1] - runtimes[0])/60.0
            print("runtime difference between largest and smallest:", round(duration_min, 2))
            fig, ax = plt.subplots()
            #runtimes = [runtime/(86400.0*30) for runtime in runtimes]
            runtimes = [runtime/(60.0*60) for runtime in runtimes]
            sensors = [labels[sensor] if sensor in labels else sensor.capitalize() for sensor in sensors]
            rects = ax.barh(sensors, runtimes, height=0.7, fill=False, hatch="////", log=True)
            autolabel(ax, rects)
            ax.set_xlabel("Runtime (hour)")
            ax.xaxis.grid(True, linestyle="dotted")
            # due to log scale set_xticks([]) does not work
            ax.xaxis.set_minor_formatter(NullFormatter())
            ax.xaxis.set_major_formatter(NullFormatter())
            fig.set_figheight(fig.get_figheight()*1.4)
            filename = "energy-runtime." + plot_format
            fig.savefig(os.path.join(result_path, filename), format=plot_format, bbox_inches="tight")
            #plt.show()
            plt.close(fig)
        
        idle_path = os.path.join(idle_path, filename_idle)
        idle_measurements = DillSerializer(idle_path).deserialize()
        
        I_mA = numpy.mean(idle_measurements.currents)
        U_V = numpy.mean(idle_measurements.voltages)
        I_A = I_mA / 1000.0
        
        Q_battery_mAh = 2800
        E_battery_Wh = (Q_battery_mAh * U_V) / 1000.0 # 1 Wh = 3600 Ws = 3600 J, W = V*A
        E_battery_J = E_battery_Wh * 3600
        idle_time_h = E_battery_Wh / (U_V * I_A) # V*A*h/V*A = h, J/V*A = Ws/V*A, V*A*s/V*A = s
        
        print("energy battery (J):", round(E_battery_J, 2))
        print("idle time (h):", round(idle_time_h, 2))
        
        sensor_sampling_rates = {"bluetooth": 300,
                                 "barometer": 300,
                                 "magnetometer": 300,
                                 "ble": 300,
                                 "gsm": 300,
                                 "gps": 300,
                                 "wifi": 300,
                                 "light": 300,
                                 "accelerometer": 5,
                                 "location-network": 300}
        
        sensors = list()
        idle_energy = list()
        sensor_energy = list()
        idle_energy_ratio = list()
        sensor_energy_ratio = list()
        runtimes_sensor = list()
        runtimes_idle_sensor = list()
        
        sensor_energies_mJ = sorted(sensor_energies_mJ.items(), key=lambda kv: kv[1])
        sensor_energies_mJ = collections.OrderedDict(sensor_energies_mJ)
        for sensor_name, sensor_energy_mJ in sensor_energies_mJ.items():
            sensor_sampling_rate_s = sensor_sampling_rates[sensor_name]
            E_sensor_J = sensor_energy_mJ / 1000.0
            # runtime idle + sensor action
            idle_sensor_runtime_s = (E_battery_J * sensor_sampling_rate_s) / ( (U_V * I_A * sensor_sampling_rate_s) + E_sensor_J )
            # only runtime for sensor action
            sensor_runtime_s = (E_battery_J * sensor_sampling_rate_s) / E_sensor_J
            
            idle_energy_J = U_V * I_A * idle_sensor_runtime_s
            sensor_energy_J = E_sensor_J * (idle_sensor_runtime_s / sensor_sampling_rate_s)
            
            sensors.append(sensor_name)
            idle_energy.append(idle_energy_J)
            sensor_energy.append(sensor_energy_J)
            idle_energy_ratio.append(idle_energy_J / E_battery_J)
            sensor_energy_ratio.append(sensor_energy_J / E_battery_J)
            runtimes_sensor.append(sensor_runtime_s)
            runtimes_idle_sensor.append(idle_sensor_runtime_s)
            
            print(sensor_name)
            print("energy battery (J):", round(E_battery_J, 2))
            print("idle energy (J):", round(idle_energy_J, 2))
            print("sensor energy (J):", round(sensor_energy_J, 2))
            print("total energy (J):",  round(idle_energy_J + sensor_energy_J, 2))
            print("runtime idle sensor (h):", round(idle_sensor_runtime_s / 3600.0, 2))
            print("runtime sensor (day):", round(sensor_runtime_s / 86400.0, 2))
        
        #plot_runtime(sensors, runtimes_sensor, labels, result_path, plot_format)
        plot_runtime(sensors, runtimes_idle_sensor, labels, result_path, plot_format)
        plot_ratio_idle_sensor_energy(sensors, idle_energy, sensor_energy, idle_energy_ratio, sensor_energy_ratio)
        
    plot_format = "pdf"
    labels = {"wifi": "Wi-Fi scan",
              "location-network": "Location Network",
              "bluetooth": "Bluetooth discovery",
              "gps": "Location GPS",
              "ble": "BLE scan",
              "gsm": "GSM scan",
              "light": "Light reading",
              "magnetometer": "Magnetometer reading",
              "accelerometer": "Accelerometer reading",
              "barometer": "Barometer reading"}
    result_path = os.path.join(__location__, "paper-results")
    
    print("### comparison over entire time frame")
    calculate_energy_per_reading_old(measurements_path)
    
    print("### energy per time slice")
    sensors, energy_mean_mJ, energy_std_mJ, energy_median_mJ = calculate_energy_per_reading(measurements_path)
    
    print("### battery lifetime")
    sensor_energies_mJ = dict(zip(sensors, energy_median_mJ))
    battery_lifetime(measurements_path, sensor_energies_mJ, labels, result_path, plot_format)
    
    plot_sensor_energy(sensors, energy_mean_mJ, energy_std_mJ, labels, result_path, plot_format)
    
    print("### energy clusters")
    identify_energy_clusters(sensors, energy_median_mJ)
    
    print("### energy comparison")
    energy_median_sensors = sorted(zip(sensors, energy_mean_mJ), key=lambda x: x[1])
    for (sensor1, energy1), (sensor2, energy2) in pairwise(energy_median_sensors):
        print(sensor2, sensor1, "multiple", round((energy2 / energy1), 2))
    for (sensor1, energy1), (sensor2, energy2) in pairwise([energy_median_sensors[0], energy_median_sensors[-1]]):
        print(sensor2, sensor1, "multiple", round((energy2 / energy1), 2))
    
def main():
    analysis = True
    result_path = os.path.join(__location__, "energy-measurements")
    if analysis:
        #generate_dummy_data_temp_humidity(result_path)
        analyze_measurements(result_path)
    else:
        perform_measurements(result_path)
    
if __name__ == "__main__":
    main()
    