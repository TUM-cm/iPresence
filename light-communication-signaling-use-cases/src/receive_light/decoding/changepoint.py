import numpy
import receive_light.decoding.smoothing as smoothing

def find_changepoints(smoothed_data):
    changepoints = numpy.diff(smoothed_data)
    changepoint_idx = numpy.where(numpy.logical_or(changepoints==1, changepoints==-1))
    return changepoint_idx[0]

def count_changepoints(changepoints, peaks_changepoint=2):
    diff = numpy.diff(changepoints)
    changes = numpy.count_nonzero(diff)
    return changes / peaks_changepoint

def count_changepoints_loop(changepoints):
    peaks_changepoint = 2
    prev = 0
    count = 0
    for value in changepoints:
        if value != prev:
            count += 1
        prev = value
    return count / peaks_changepoint

def find_window_size(data, changepoints_threshold=5):
    size = 0
    step_count = 0
    step_sizes = [i*10**exp for exp in range(2, 9) for i in range(1, 10)] # exponential growth
    num_changepoints = 0
    mean = numpy.mean(data)
    max_size = len(data)
    while num_changepoints < changepoints_threshold:
        size += step_sizes[step_count]
        if size > max_size:
            size = max_size
            break
        subdata = data[:size]
        smoothed_data = smoothing.simple(subdata, mean)
        num_changepoints = count_changepoints(smoothed_data)
        step_count += 1
    return size
