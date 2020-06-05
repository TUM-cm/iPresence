#!/usr/bin/env python

from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext

import numpy

# python setup.py build_ext --inplace

setup(
    cmdclass = {'build_ext': build_ext},
    ext_modules = [Extension("test_array",
                             sources=["array.pyx", "c_array.c"],
                             include_dirs=[numpy.get_include()])],
)