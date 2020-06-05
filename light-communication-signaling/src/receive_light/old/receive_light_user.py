import os
import mmap
import numpy
import struct
import subprocess

from utils.vlc_interfaces import ReceiverAction
from utils.vlc_interfaces import ReceiverDevice

class LightReceiverControl():
    
    def __init__(self, control_program="control_light_receiver"):
        self.control_program = control_program
        self.args = [ReceiverDevice.pd, 20000]
        self.page_size = None
        self.num_pages = None
    
    def set_device(self, device):
        self.args[0] = device
    
    def set_sampling_frequency(self, sampling_frequency):
        self.args[1] = sampling_frequency
    
    def start(self):
        command = ["./" + self.control_program, ReceiverAction.start] + self.args
        command = [str(e) for e in command]
        print command
        out = subprocess.check_output(command)
        print out
        for line in out:
            if "page_size" in line:
                self.page_size = line.split("=")[1]
            if "num_pages" in line:
                self.num_pages = line.split("=")[1]
    
    def stop(self):
        command = ["./" + self.control_program, ReceiverAction.stop]
        print command
        subprocess.call(command)
        
    def get_page_size(self):
        return self.page_size
    
    def get_num_pages(self):
        return self.num_pages

DATA_FORMAT = numpy.dtype([('voltage', 'i4'), ('time', 'u4')], align=True)

def data_loop():
    light_receiver_control = LightReceiverControl()
    light_receiver_control.start()
    num_pages = light_receiver_control.get_num_pages()
    page_size = light_receiver_control.get_page_size()
    
#     page = 0
#     page_offset = 0
#     prev = -1
#     while True:
#         if last_page_offset != prev:
#             # read light signal
#             page_offset += page_size
#             page += 1
#             prev = last_page_offset
#             if page == num_pages:
#                 page = 0
#                 page_offset = 0

# surface = numpy.ndarray((320,240), numpy.uint16, buf)
# 
# fp = numpy.memmap(data_file, dtype="float32", mode="r", shape=(3,4))
#     page = 0;
#     page_offset = 0;
#     prev = -1;
#     while(fast_atoi(control)) {
#         if (data->latest_page_offset != prev) {
#             memcpy(buffer, &data->buffer[page_offset], buffer_size);
#             pubmsg.payload = buffer;
#             MQTTClient_publishMessage(client, TOPIC, &pubmsg, &token);
#             page_offset += page_size;
#             page++;
#             prev = data->latest_page_offset;
#             if (page == num_pages) {
#                 page = 0;
#                 page_offset = 0;
#             }
#         }
#     }
    
    
def test_receiver_control():
    light_receiver_control = LightReceiverControl()
    light_receiver_control.start()
    light_receiver_control.stop()

def main():
    data_loop()
    #test_receiver_control()

if __name__ == "__main__":
    main()