import os
import numpy
import datetime

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

def get_microseconds(entry):
    start = entry.index(",")+1
    end = entry.index("+")
    value = entry[start:end]    
    return int(value)

def get_iso_time_str(entry):
    end = entry.index("+")
    return entry[:end]

def get_data_amount_time(entry):
    values = entry.split(" ", 1)[1].split(",")
    return [value.split(":")[1].strip() for value in values]

def create_datetime(iso_str):
    return datetime.datetime.strptime(iso_str, "%Y-%m-%dT%H:%M:%S,%f")

def get_duration_monotonic(filename):
    durations = []
    f = open(os.path.join(__location__, "data", filename), "r")
    content = f.readlines()
    data_provider = (content[i:i+2] for i in range(0, len(content)-1, 1))
    for entry in data_provider:
        data_amount = int(get_data_amount_time(entry[1])[0])
        t1_logtime = create_datetime(get_iso_time_str(entry[1]))
        t0_logtime = create_datetime(get_iso_time_str(entry[0]))
        t1_monotonic_time = int(get_data_amount_time(entry[1])[1])
        t0_monotonic_time = int(get_data_amount_time(entry[0])[1])
        durations.append((data_amount,
                          (t1_logtime - t0_logtime).microseconds, # .total_seconds()
                          t1_monotonic_time - t0_monotonic_time))
    return durations

def get_duration_system_monotonic(filepath):
    durations = []
    f = open(filepath, "r")
    content = f.readlines()
    data_provider = (content[i:i+2] for i in range(0, len(content)-1, 1))
    for entry in data_provider:
        data_amount = int(get_data_amount_time(entry[1])[0])
        t1_logtime = create_datetime(get_iso_time_str(entry[1]))
        t0_logtime = create_datetime(get_iso_time_str(entry[0]))
        t1_system_time = int(get_data_amount_time(entry[1])[1])
        t0_system_time = int(get_data_amount_time(entry[0])[1])
        t1_monotonic_time = int(get_data_amount_time(entry[1])[2])
        t0_monotonic_time = int(get_data_amount_time(entry[0])[2])
        durations.append((data_amount,
                          (t1_logtime - t0_logtime).microseconds, # .total_seconds()
                          t1_system_time - t0_system_time,
                          t1_monotonic_time - t0_monotonic_time))
    return durations

def get_dummy_duration(filepath):
    durations = []
    f = open(filepath, "r")
    content = f.readlines()
    data_provider = (content[i:i+2] for i in range(0, len(content)-1, 1))
    for entry in data_provider:
        t1 = create_datetime(get_iso_time_str(entry[1]))
        t0 = create_datetime(get_iso_time_str(entry[0]))
        duration = t1 - t0
        durations.append(duration.microseconds)
    return durations

def log_output(header, durations):
    print(header)
    print("num values: ", len(durations))
    print("mean (us): ", numpy.mean(durations))
    print("median (us): ", numpy.median(durations))
    print("std (us): ", numpy.std(durations))
    print("min (us): ", numpy.min(durations))
    print("max (us): ", numpy.max(durations))
    print("range of changes (us): ", numpy.max(durations) - numpy.min(durations))
    print("range of changes (%): ", 100 * (numpy.max(durations) - numpy.min(durations)) / float(numpy.max(durations)))
    print("---------------------------------")

def test_realtime_system(folder):
    data_entries = [(folder + "10us", "10 us, 10.000 values = 100.000 us"),
                    (folder + "20us", "20 us, 10.000 values = 200.000 us")]
    for entry in data_entries:
        filename = entry[0]
        header = entry[1]
        duration = get_dummy_duration(filename)
        log_output(header, duration)

def test_different_clocks(folder):
    data_filepath = os.path.join(folder, "time_data_speed_all_clocks")
    durations = get_duration_system_monotonic(data_filepath)
    print("logging: ", numpy.mean([duration[1] for duration in durations]))
    print("system: ", numpy.mean([duration[2] for duration in durations]) / 1000.0) # ns to us
    print("monotonic: ", numpy.mean([duration[3] for duration in durations]) / 1000.0)

if __name__ == '__main__':
    # dmesg --time-format=iso
    folder = "./data/"
    test_realtime_system(folder)
    test_different_clocks(folder)
