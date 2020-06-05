import os
import mmap
import ctypes

data_file = "/sys/kernel/debug/light_signal"
 
'''
struct data
{
    int latest_page_offset;
    struct buffer buffer[MAX_BUFFER_SIZE];
};
 
struct buffer
{
    int voltage;
    unsigned int time;
};
 
struct data *data = NULL;
length_data = sizeof(int) + (num_pages * page_size) * sizeof(struct buffer);
data = mmap(0, length_data, PROT_READ, MAP_SHARED, data_fd, 0);
'''

num_pages = 103
page_size = 10000
max_buffer_size = num_pages * page_size
 
class buf_element(ctypes.Structure):
     
    _fields_ = [("voltage", ctypes.c_int),
        ("time", ctypes.c_uint)]
 
class data(ctypes.Structure):
     
    _fields_ = [("latest_page_offset", ctypes.c_int),
                ("buffer", ctypes.POINTER(buf_element))]
 
length_data = ctypes.sizeof(ctypes.c_int) + max_buffer_size * ctypes.sizeof(buf_element);
fd = os.open(data_file, os.O_RDWR)
buf = mmap.mmap(fd, length_data, mmap.MAP_SHARED, mmap.PROT_READ)
test_data = data.from_buffer(buf)
print test_data.latest_page_offset
os.close(fd)
