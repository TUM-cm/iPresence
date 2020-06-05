from distutils.core import setup, Extension

# call: python setup.py install as root

setup(name="light_receiver", version="0.0",
    ext_modules = [Extension("light_receiver", ["receive_light_user.c"])])