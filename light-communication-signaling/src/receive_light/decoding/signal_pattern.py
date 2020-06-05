from __future__ import division
import numpy

def calculate_time_base_unit(changepoints, time, peak_idx):
    start = peak_idx[0]
    stop = peak_idx[1]
    duration = time[stop] - time[start]
    samples = len(changepoints[start+1:stop+1])
    return duration/samples

def calculate_time_base_unit_abs(changepoints, time):
    start = changepoints[0]
    stop = changepoints[1]
    duration = time[stop] - time[start]
    return duration

def calculate_pattern(changepoint_idx, smoothed_data, time,
                      time_base_unit=1, abs_duration=True, start=0, stop=1):
    sequences = []
    changepoints = (changepoint_idx[i:i+2] for i in range(0, len(changepoint_idx)-1, 1))
    for changepoint in changepoints:
        changepoint_start = changepoint[start]
        changepoint_stop = changepoint[stop]
        time_start = time[changepoint_start]
        time_stop = time[changepoint_stop]
        duration = time_stop - time_start
        if abs_duration:
            phase = smoothed_data[changepoint_start+1:changepoint_stop+1]
            unique = numpy.unique(phase)
            if len(unique) == 1:
                sequences.append((int(unique[0]), duration))
        else:
            units = duration / time_base_unit
            phase = smoothed_data[changepoint_start+1:changepoint_stop+1]
            unique = numpy.unique(phase)
            if len(unique) == 1:
                sequences.append((int(unique[0]), units))
    return sequences

def plausibility_check(pattern):
    for i, entry in enumerate(pattern):
        if (i+1) < len(pattern):     
            if entry[0] == pattern[i+1][0]:
                print "error"
