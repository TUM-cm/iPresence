import numpy
import pylab
import timeit
from scipy import stats

# data
y = numpy.array([80,80,80,80,80,80,80,80,80,80,80,80,120,120,120,120,120,120,120,120,120,120,120,120,
              80,80,80,80,80,80,80,80,80,80,80,80,120,120,120,120,120,120,120,120,120,120,120,120,
              80,80,80,80,80,80,80,80,80,80,80,80])

def using_where():
    zscores = stats.zscore(y)
    changepoints = numpy.ma.masked_where(zscores>0, zscores)
    zscores[changepoints.mask] = 1
    zscores[~changepoints.mask] = 0
    return zscores

def using_loop():
    zscores = stats.zscore(y)
    for i, entry in enumerate(zscores):
        if entry > 0:
            zscores[i] = 1
        else:
            zscores[i] = 0
    return zscores

def plot(y, zscores):
    pylab.subplot(211)
    pylab.plot(numpy.arange(1, len(y)+1), y)
    
    pylab.subplot(212)
    pylab.step(numpy.arange(1, len(y)+1), zscores, color="red", lw=2)
    pylab.ylim(-1.5, 1.5)
    pylab.show()

#plot(y, using_loop())
#plot(y, using_where())

# print "using where"
# where = timeit.timeit("using_where()", "from __main__ import using_where", number=1000)
# print where
# 
# print "using loop"
# loop = timeit.timeit("using_loop()", "from __main__ import using_loop", number=1000)
# print loop
# 
# print "diff rel: ", loop/where
# print "diff abs: ", where - loop


setup = '''
import numpy
import changepoint

y = numpy.array([80,80,80,80,80,80,80,80,80,80,80,80,120,120,120,120,120,120,120,120,120,120,120,120,
              80,80,80,80,80,80,80,80,80,80,80,80,120,120,120,120,120,120,120,120,120,120,120,120,
              80,80,80,80,80,80,80,80,80,80,80,80])

threshold = numpy.mean(y)

'''

repeat = 1000

print "simple threshold: loop"
print timeit.timeit("changepoint.simple_threshold(y, changepoint.Threshold.mean)", setup=setup, number=repeat)

print "simple threshold: where"
print timeit.timeit("changepoint.simple_threshold_where(y, changepoint.Threshold.mean)", setup=setup, number=repeat)

print "-------------------"

print "zscore threshold: loop"
print timeit.timeit("changepoint.zscore_threshold(y)", setup=setup, number=repeat)

print "zscore threshold: where"
print timeit.timeit("changepoint.zscore_threshold_where(y)", setup=setup, number=repeat)

print "-------------------"

print "fixed threshold: loop"
print timeit.timeit("changepoint.simple_fixed_threshold(y, threshold)", setup=setup, number=repeat)

print "fixed threshold: where"
print timeit.timeit("changepoint.simple_fixed_threshold_where(y, threshold)", setup=setup, number=repeat)

print "-------------------"

print "cusum"
print timeit.timeit("changepoint.cusum_threshold(y, changepoint.Threshold.mean)", setup=setup, number=repeat)


setup = '''
import numpy
import changepoint
import offline_evaluation

y = numpy.array([80,80,80,80,80,80,80,80,80,80,80,80,120,120,120,120,120,120,120,120,120,120,120,120,
              80,80,80,80,80,80,80,80,80,80,80,80,120,120,120,120,120,120,120,120,120,120,120,120,
              80,80,80,80,80,80,80,80,80,80,80,80])
threshold = numpy.mean(y)
changepoints = changepoint.simple_fixed_threshold_where(y, threshold)
'''

print "count changepoints"
print timeit.timeit("offline_localvlc_evaluation.count_changepoints(changepoints)", setup=setup, number=10000)

print "count changepoints loop"
print timeit.timeit("offline_localvlc_evaluation.count_changepoints_loop(changepoints)", setup=setup, number=10000)
