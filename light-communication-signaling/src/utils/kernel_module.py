import os
import sys
import logging
import subprocess

SEND_KERNEL_MODULE = "send_light_kernel.ko"
RECEIVE_KERNEL_MODULE = "receive_light_kernel.ko"

def get_name(module_filename):
    return module_filename.split(".")[0]

def insert(kernel_module, cwd=None):
    out = subprocess.check_output("lsmod")
    if get_name(kernel_module) not in out:
        if cwd:
            if not os.path.isfile(cwd + kernel_module):
                sys.exit("\nKernel module: " + cwd + kernel_module + " is not available\n")
        else:
            if not os.path.isfile(kernel_module):
                sys.exit("\nKernel module: " + kernel_module + " is not available\n")
        if cwd:
            result = subprocess.call("insmod " + kernel_module, shell=True, cwd=cwd)
        else:    
            result = subprocess.call("insmod " + kernel_module, shell=True)
        if result != 0:
            sys.exit("\nKernel module not inserted\n")

def remove(kernel_module):
    out = subprocess.check_output("lsmod")    
    if get_name(kernel_module) in out:
        result = subprocess.call("rmmod " + kernel_module, shell=True)
        if result != 0:
            sys.exit("\nKernel module is not removed\n")

def add_light_receiver():
    directory_receive_module = "receive_light/"
    library_name = "light_receiver.so"
    kernel_module_receive_light = directory_receive_module + RECEIVE_KERNEL_MODULE
    library_receive_light = directory_receive_module + library_name
    logging.info("make kernel modules")
    if not os.path.isfile(kernel_module_receive_light):
        subprocess.call("make", shell=True, cwd=directory_receive_module)
    if not os.path.isfile(library_receive_light):
        subprocess.call("make interface", shell=True, cwd=directory_receive_module)
    logging.info("insert kernel module")
    insert(RECEIVE_KERNEL_MODULE, cwd=directory_receive_module)

def add_light_sender():
    directory_send_module = "send_light/"
    kernel_module_send_light = directory_send_module + SEND_KERNEL_MODULE
    logging.info("make kernel module")
    if not os.path.isfile(kernel_module_send_light):
        subprocess.call("make", shell=True, cwd=directory_send_module)
