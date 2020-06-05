import numpy
from scipy import stats
from utils.custom_enum import enum_name

Threshold = enum_name("mid_range", "median", "mean")

def get_threshold_value(data, threshold_type):
    if threshold_type == Threshold.mid_range:
        min_val = numpy.min(data)
        max_val = numpy.max(data)
        threshold = min_val + ((max_val - min_val)/2)
    elif threshold_type == Threshold.median:
        threshold = numpy.median(data)
    elif threshold_type == Threshold.mean:
        threshold = numpy.mean(data)
    return threshold

def cusum(data, threshold_type=Threshold.mean):
    likelihood = get_threshold_value(data, threshold_type)
    cusum = numpy.empty(data.shape[0])
    cusum_val = 0
    for i in range(data.shape[0]):
        cusum_val = max(0, cusum_val + data[i] - likelihood)
        cusum[i] = cusum_val
    diff = numpy.diff(cusum)
    high = numpy.where(diff > 0)
    low = numpy.where(diff < 0)
    diff[high] = 1
    diff[low] = 0
    diff.resize(data.shape[0], refcheck=False)
    diff[-1] = diff[-2]
    return diff

def simple(data, threshold):
    changepoints = numpy.zeros(len(data))
    high = numpy.where(data > threshold)
    changepoints[high] = 1
    return changepoints

def simple_threshold(data, threshold_type=Threshold.mean):
    threshold = get_threshold_value(data, threshold_type)
    changepoints = numpy.zeros(len(data), dtype=numpy.int32)
    high = numpy.where(data > threshold)
    changepoints[high] = 1
    return changepoints

# z-score: current value is how many standard deviations away from the mean
# formula: z_i = (x_i - mean) / std
def zscore(data):
    zscores = stats.zscore(data)    
    for i, entry in enumerate(zscores):
        if entry > 0:
            zscores[i] = 1
        else:
            zscores[i] = 0
    return zscores

def zscore_where(data):
    zscores = stats.zscore(data)
    high = numpy.where(zscores > 0)
    low = numpy.where(zscores < 0)
    zscores[high] = 1
    zscores[low] = 0
    return zscores
