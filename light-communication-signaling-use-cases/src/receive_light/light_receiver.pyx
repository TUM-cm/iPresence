import cython
import numpy as np
cimport numpy as np
# https://github.com/cython/cython/wiki/FAQ
#from cpython cimport bool

cdef extern from "callback.h":
    ctypedef void (*streamfunc)(int* voltage, unsigned int* time, void *user_data)

cdef extern int c_start(char *device, int interval, int logging)
cdef extern int c_stop()
cdef extern void c_start_stream(streamfunc user_func, void *user_data)
cdef extern int c_stop_stream()
cdef extern void c_get_data_copy(int* voltage, unsigned int* time)
cdef extern void c_get_data_ptr(int* voltage, unsigned int* time)
cdef extern int c_get_num_pages()
cdef extern int c_get_page_size()
cdef extern int c_get_cur_data_idx()
cdef extern int c_get_prev_data_idx()
cdef extern int c_calc_page_size(int interval)

def start(device, sampling_interval, logging):
    cdef int ret
    ret = c_start(device, sampling_interval, int(logging))
    return ret

def stop():
    cdef int ret
    ret = c_stop()
    return ret

def get_num_pages():
    cdef int ret
    ret = c_get_num_pages()
    return ret
    
def get_page_size():
    cdef int ret
    ret = c_get_page_size()
    return ret

def get_cur_data_idx():
    cdef int ret
    ret = c_get_cur_data_idx()
    return ret

def get_prev_data_idx():
    cdef int ret
    ret = c_get_prev_data_idx()
    return ret

@cython.boundscheck(False)
@cython.wraparound(False)
def get_data_copy(np.ndarray[int, ndim=1, mode="c"] voltage,
                  np.ndarray[unsigned int, ndim=1, mode="c"] time):
    c_get_data_copy(&voltage[0], &time[0])
    return None

@cython.boundscheck(False)
@cython.wraparound(False)
def get_data_ptr(np.ndarray[int, ndim=1, mode="c"] voltage,
                 np.ndarray[unsigned int, ndim=1, mode="c"] time):
    c_get_data_ptr(&voltage[0], &time[0])
    return None

def start_stream(device, sampling_interval, callback, logging):
    start(device, sampling_interval, logging)
    c_start_stream(callback_stream, <void*> callback)

cdef void callback_stream(int* voltage, unsigned int* time, void *callback):
    # https://github.com/cython/cython/tree/master/Demos/callback
    cdef int[:] mem_view_voltage = <int[:get_page_size()]> (voltage)
    cdef unsigned int[:] mem_view_time = <unsigned int[:get_page_size()]> (time)
    voltage_array = np.asarray(mem_view_voltage)
    time_array = np.asarray(mem_view_time)
    (<object>callback)(voltage_array, time_array)

def stop_stream():
    cdef int ret
    ret = c_stop_stream()
    return ret

def calc_page_size(sampling_interval):
    cdef int ret
    ret = c_calc_page_size(sampling_interval)
    return ret
