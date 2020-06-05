import numpy
from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext

# make interface
# cython generates from *.pyx and *.c file
# Never use the same name for *.pyx and *.c file containing code
# > Leads to multiple method definition errors
# python setup.py build_ext --inplace

setup(
    cmdclass = {'build_ext': build_ext},
    ext_modules = [Extension("light_receiver",
                             sources=["light_receiver.pyx", "c_light_receiver.c"],
                             include_dirs=[numpy.get_include()],
                             extra_compile_args=['-lm']
                             )
                   ],
)
