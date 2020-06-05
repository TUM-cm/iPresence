import timeit

setup = '''
import numpy

a = numpy.array([1,2,3,4,5])
c = a.tolist()
'''

#print timeit.timeit("''.join(map(str, c))", setup=setup, number=1000000)
#print timeit.timeit("filter(str.isdigit, repr(c))", setup=setup, number=1000000)
#print timeit.timeit("reduce(lambda x,y: x+str(y), c, '')", setup=setup, number=1000000)

'''
0.886890049265
2.05344748929
1.49376348855
'''

setup = '''
import numpy
#zeros = numpy.zeros(1000)
#ones = numpy.zeros(1000)
#a = numpy.hstack([zeros, ones, zeros, ones, zeros, ones, zeros, ones])
a = numpy.array([1,1,0,1,1])
'''

test1 = '''
one_idx = numpy.where(a==1)
zero_idx = numpy.where(a==0)
a[one_idx] = 100
a[zero_idx] = 200
'''

test2 = '''
one_mask = a == 1
a[one_mask] = 100
a[~one_mask] = 200
'''

print timeit.timeit(test1, setup=setup, number=1000000)
print timeit.timeit(test2, setup=setup, number=1000000)
