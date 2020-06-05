from __future__ import division
import os
import json
import time
import numpy
import random
import logging
import localvlc.files as files

plot_show = False
plot_grid_linestyle = "dotted"
matplotlib_font_size = 22
try:
    import matplotlib
    import matplotlib.pyplot as plt
    font = {'size' : matplotlib_font_size}
    matplotlib.rc('font', **font)
    matplotlib.rcParams['pdf.fonttype'] = 42 # TrueType
    matplotlib.rcParams['ps.fonttype'] = 42 # TrueType
    #matplotlib.rcParams['text.usetex'] = True # type1, different fonts
except:
    pass

def get_idx_outliers(data, m=2):
    return abs(data - numpy.mean(data)) <= m * numpy.std(data)
    
def reject_outliers(data, m=2):
    return data[get_idx_outliers(data, m)]

def read_json(f):
    return json.loads(f.read())

def get_name(f):
    basename = os.path.basename(f.name)
    return basename.split(".")[0]

def open_file(filename, directory=files.dir_results, mode="r"):
    path = find(filename, directory)
    if path != None:
        return open(path, mode) 

def find(name, directory=files.dir_results):
    for root, _, files in os.walk(directory):        
        for f in files:
            if name in f:
                return os.path.join(root, f)

def savefig(subdir, filename, ending="eps", transparent=True):
    if plot_show:
        plt.show()
    else:
        path = files.dir_statistics + subdir + filename + "." + ending
        if not os.path.exists(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path))
        plt.savefig(path, format=ending, bbox_inches="tight", transparent=transparent)
        plt.close()

def ratio(subset, all_set):
    return subset / all_set

def autolabel(rects):
    for rect in rects:
        height = rect.get_height()
        x = rect.get_x() + rect.get_width()/2.
        y = height
        plt.text(x, y, '%d' % int(height), ha='center', va='bottom')

def log(data, subdir, filename, ending=".txt"):
    filename = filename.split(".")[0]
    path = files.dir_statistics + subdir + "/" + filename + ending
    if not os.path.exists(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))
    f = open(path, "w")
    f.write(data)
    f.close()
    
def create_test_data_token_distribution():
    formatter = logging.Formatter('%(asctime)s.%(msecs)03d: %(message)s', datefmt="%H:%M:%S")
    name = "broadcast_token"
    logger_broadcast_token = logging.getLogger(name)
    logger_broadcast_token.setLevel(logging.INFO)
    fh_sender = logging.FileHandler(name + ".log")
    fh_sender.setFormatter(formatter)
    logger_broadcast_token.addHandler(fh_sender)
    name = "receive_token"
    logger_receive_token = logging.getLogger(name)
    logger_receive_token.setLevel(logging.INFO)
    fh_receiver = logging.FileHandler(name + ".log")
    fh_receiver.setFormatter(formatter)
    logger_receive_token.addHandler(fh_receiver)
    counter = 0
    repeat = 10
    sleeps = list()
    while counter < repeat:
        token = random.randint(111111, 999999) # random 6-digit number
        logger_broadcast_token.info(token)
        sleep_period = random.randint(1, 9)
        sleeps.append(sleep_period)
        time.sleep(sleep_period)
        logger_receive_token.info(token)
        counter += 1
    print(sleeps)
    