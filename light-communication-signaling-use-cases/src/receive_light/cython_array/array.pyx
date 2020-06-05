import cython

import numpy as np
cimport numpy as np

cdef extern void c_set_array (int* voltage, int volt_shape, unsigned int* time, int time_shape)
cdef extern void c_copy_array (int* voltage, int volt_shape, unsigned int* time, int time_shape)

@cython.boundscheck(False)
@cython.wraparound(False)
def set_data(np.ndarray[int, ndim=1, mode="c"] voltage not None,
             np.ndarray[unsigned int, ndim=1, mode="c"] time not None):
    
    cdef int volt_shape, time_shape

    volt_shape = voltage.shape[0]
    time_shape = time.shape[0]
    
    c_set_array (&voltage[0], volt_shape, &time[0], time_shape)

    return None

@cython.boundscheck(False)
@cython.wraparound(False)
def copy_data(np.ndarray[int, ndim=1, mode="c"] voltage not None,
              np.ndarray[unsigned int, ndim=1, mode="c"] time not None):
    
    cdef int volt_shape, time_shape

    volt_shape = voltage.shape[0]
    time_shape = time.shape[0]
    
    c_copy_array (&voltage[0], volt_shape, &time[0], time_shape)

    return None
