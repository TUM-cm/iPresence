from __future__ import division
import numpy
import timeit
import pandas as pd
import scipy.stats as sc

def get_summary(data, digits=2):
    return "num: " + str(len(data)) + "\n" + \
        "min. " + str(round(numpy.min(data), digits)) + "\n" + \
        "max: " + str(round(numpy.max(data), digits)) + "\n" + \
        "median: " + str(round(numpy.median(data), digits)) + "\n" + \
        "mean: " + str(round(numpy.mean(data), digits)) + "\n" + \
        "std: " + str(round(numpy.std(data), digits)) + "\n" + \
        "var: " + str(round(numpy.var(data), digits))

def unique(data, dtype=numpy.int64):
    unique, counts = numpy.unique(data, return_counts=True)
    return numpy.asarray((unique, counts), dtype=dtype).T

def bincount(data):
    counts = numpy.bincount(data)
    val_idx = numpy.nonzero(counts)[0]
    return numpy.vstack((val_idx, counts[val_idx])).T

def histogram(data):
    data = numpy.array(data).astype(numpy.int)
    hist, bin_edges = numpy.histogram(data, bins='auto')
    return hist, bin_edges

# Shannon entropy: H(x) = -sum(p(i)*log_2(p(i)))
def entropy(data): # uncertainty, information gain
    _, counts = numpy.unique(data, return_counts=True)
    pk = counts / data.shape[0]
    return -numpy.sum(pk * numpy.log(pk))
    #return -numpy.sum(pk * numpy.log2(pk))
    #return scipy.stats.entropy(pk, base=2)
    
def entropy_pandas(data):
    data = pd.Series(data)
    p_data = data.value_counts()/len(data) # calculates the probabilities
    entropy = sc.entropy(p_data)  # input probabilities to get the entropy 
    return entropy

# normalize
#     min, max
#     max mult    equal if input range starts from 0, only upper limit
#     sum            upper and lower adaption but much smaller range

def min_max_norm(x):
    min_val = x.min()
    return (x - min_val) / (x.max() - min_val)

def max_norm(x, upper_limit=1.0):
    x *= upper_limit / x.max()
    return x

def sum_norm(x):
    return x / numpy.sum(x, axis=0)

def linalg_norm(x):
    return x / numpy.linalg.norm(x, axis=0)

def standardize(x):
    return (x - x.mean()) / x.std()

def performance_norm_test():
    setup = '''
    import numpy
    
    min_val = 100
    max_val = 500
    data_len = 10000
    
    voltage = numpy.random.randint(min_val, max_val, data_len)
    voltage_float = numpy.random.randint(min_val, max_val, data_len).astype('float')
    '''
    
    repeat = 10000
    
    execute = '''
    min_val = voltage.min()
    voltage = (voltage - min_val) / (voltage.max() - min_val)
    '''
    print("min max")
    print(timeit.timeit(execute, setup=setup, number=repeat))
    
    execute = '''
    voltage_float *= 1.0/voltage_float.max()
    '''
    print("max mult")
    print(timeit.timeit(execute, setup=setup, number=repeat))
    
    execute = '''
    voltage = 1.0*voltage / numpy.sum(voltage, axis=0)
    '''
    print("sum")
    print(timeit.timeit(execute, setup=setup, number=repeat))
    
    execute = '''
    voltage = voltage / numpy.linalg.norm(voltage)
    '''
    print("norm")
    print(timeit.timeit(execute, setup=setup, number=repeat))
