import logging

def activate_file_console(filename):
    level = logging.INFO
    fmt = '%(asctime)s %(message)s'
    logging.basicConfig(format=fmt, level=level, filename=filename + ".log", filemode="w")
    console = logging.StreamHandler()
    console.setLevel(level)
    formatter = logging.Formatter(fmt)
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)

def activate_info():
    logging.getLogger().setLevel(logging.INFO)

def activate_debug():
    logging.getLogger().setLevel(logging.DEBUG)
