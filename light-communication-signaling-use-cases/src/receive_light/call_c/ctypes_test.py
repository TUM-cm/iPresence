import ctypes
import numpy
from numpy.ctypeslib import ndpointer

# compile c program: gcc -fPIC -shared -o ctest.so ctest.c
lib = ctypes.cdll.LoadLibrary('./ctest.so')

init = lib.init
init.restype = ctypes.c_int
init.argtypes = [ctypes.c_int, ctypes.c_int]
print init(10, 20)
 
get_num_pages = lib.get_num_pages
init.restype = ctypes.c_int
print get_num_pages()
 
get_page_size = lib.get_page_size
init.restype = ctypes.c_int
print get_page_size()

# by reference for direct write
get_data = lib.get_data
init.restype = None
val = ctypes.c_int32()
init.argtypes = [ctypes.POINTER(ctypes.c_int)]
get_data(ctypes.byref(val))

test = lib.test
test.restype = None
test.argtypes = [ndpointer(ctypes.c_double, flags="C_CONTIGUOUS")]
outdata = numpy.empty((5,6))
print "before"
print outdata
test(outdata)
print "after"
print outdata